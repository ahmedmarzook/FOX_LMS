/** @odoo-module **/

import {
    Component, useState, onMounted, onWillUnmount,
    useRef, useEffect, useExternalListener,
} from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { debounce } from "@web/core/utils/timing";
import session from "@web/session";

const systrayRegistry = registry.category("systray");

export class PtGlobalTopbar extends Component {
    setup() {
        this.ui = useService("ui");
        this.menu = useService("menu");
        this.action = useService("action");
        this.notification = useService("notification");
        this.orm = useService("orm"); // ✅ available in Odoo 16+

        // ---- Safe session reads (session may be undefined in some builds)
        this.uid = session?.uid || null;

        this.userName = session?.name || session?.username || "المستخدم";
        this.userCompany = session?.company_id?.[1] || "";
        this.userAvatar = this.uid
            ? `/web/image/res.users/${this.uid}/avatar_128`
            : "/web/static/img/user_menu_avatar.png";

        this.companyId = session?.company_id?.[0] || null;
        this.companyLogo = this._buildCompanyLogo();

        this.state = useState({
            treeQuery: "",
            currentMenuId: "",
            apps: [],
            appTrees: {},
            expanded: {},
            drawerOpen: false,
            topbarUserMenuOpen: false,
            tabsExtra: [],
            tabsOverflowOpen: false,
        });

        this.tabsRef = useRef("appTabs");
        this._debouncedAdaptTabs = debounce(() => this._adaptTabs(), 150);
        useExternalListener(window, "resize", this._debouncedAdaptTabs);

        // Re-measure whenever the current app (and therefore its tab set)
        // changes. Runs after the patch, so the new tabs are already in the
        // DOM by the time we measure them.
        useEffect(
            () => {
                this._adaptTabs();
            },
            () => [this.currentAppNav?.app?.id, this.currentAppNav?.tabs?.length]
        );

        onMounted(async () => {
            // If session did not provide good info, fetch it safely
            await this._ensureUserInfo();

            this._loadApps();
            this._syncCurrentFromMenuService();

            // Refresh menus + current-app tabs when the menu service detects
            // a change — fired on boot (Odoo resolves the current app from
            // the URL itself) and whenever our own nav handlers below call
            // menu.setCurrentMenu().
            this._onMenusChanged = () => {
                this._loadApps();
                this._syncCurrentFromMenuService();
            };
            this.env.bus.addEventListener("MENUS:APP-CHANGED", this._onMenusChanged);
        });

        onWillUnmount(() => {
            if (this._onMenusChanged) {
                this.env.bus.removeEventListener("MENUS:APP-CHANGED", this._onMenusChanged);
            }
        });
    }

    // ===============================
    // Ensure user info (fallback via ORM)
    // ===============================
    async _ensureUserInfo() {
        // if uid missing, we can't fetch anything
        if (!this.uid) return;

        // if we already have name + company, stop
        if ((this.userName && this.userName !== "المستخدم") && this.userCompany) return;

        try {
            // Read user
            const users = await this.orm.read("res.users", [this.uid], ["name", "company_id"]);
            const u = users?.[0];
            if (u?.name) this.userName = u.name;

            // company_id can be [id, name] or just id depending on version
            const companyId = Array.isArray(u?.company_id) ? u.company_id[0] : u?.company_id;
            if (companyId) {
                const comps = await this.orm.read("res.company", [companyId], ["name"]);
                const c = comps?.[0];
                if (c?.name) this.userCompany = c.name;
                this.companyId = companyId;
                this.companyLogo = this._buildCompanyLogo();
            }

            // avatar (now uid is known)
            this.userAvatar = `/web/image/res.users/${this.uid}/avatar_128`;
        } catch (e) {
            console.warn("Property Theme: _ensureUserInfo failed", e);
        }
    }

    _buildCompanyLogo() {
        // Odoo serves a built-in placeholder silhouette when the company
        // has no logo set, so this always resolves to a valid image.
        return this.companyId
            ? `/web/image/res.company/${this.companyId}/logo`
            : "/web/static/img/logo2.png";
    }

    // ===============================
    // Systray Items (render all systray registry components in topbar)
    // ===============================
    get systrayItems() {
        try {
            return systrayRegistry.getAll().slice().reverse()
                .filter(item => {
                    const name = (item.Component?.name || item.Component?.template || "").toLowerCase();
                    return !name.includes("presence") &&
                           !name.includes("im_status") &&
                           !name.includes("onlinestatus") &&
                           !name.includes("online_status") &&
                           !name.includes("pwa") &&
                           !name.includes("install") &&
                           !name.includes("fullscreen") &&
                           !name.includes("homemenu") &&
                           // Odoo's own user-avatar systray item — we render
                           // our own avatar + dropdown in the top bar instead.
                           !name.includes("usermenu");
                });
        } catch (e) {
            return [];
        }
    }

    // ===============================
    // Current app → inline top-bar tabs
    // (mirrors Odoo's own navbar: when you're inside an app, its top-level
    // menus render as horizontal tabs instead of the home search bar)
    // ===============================
    get currentAppNav() {
        const menuId = this.state.currentMenuId;
        if (!menuId) return null;

        let menu;
        try {
            menu = this.menu.getMenu(menuId);
        } catch (e) {
            return null;
        }
        if (!menu || !menu.appID) return null;

        const appId = String(menu.appID);
        const app = (this.state.apps || []).find((a) => String(a.id) === appId);
        const tree = this.state.appTrees?.[appId];
        if (!app || !tree) return null;

        return { app, tabs: tree.children || [] };
    }

    isTabActive(tab) {
        const cur = String(this.state.currentMenuId || "");
        if (!cur) return false;
        if (String(tab.id) === cur) return true;
        return this._containsMenuId(tab, cur);
    }

    _containsMenuId(node, id) {
        for (const c of node.children || []) {
            if (String(c.id) === id) return true;
            if (this._containsMenuId(c, id)) return true;
        }
        return false;
    }

    // ===============================
    // Tab overflow ("+" dropdown)
    // Mirrors Odoo's own NavBar.adapt(): measure every tab's natural width
    // with all of them visible, then hide whichever trailing tabs don't fit
    // and list them in a "+" dropdown instead. Hiding is done by directly
    // toggling a CSS class on the DOM nodes (not through reactive state) so
    // re-measuring never has to fight with elements it just hid itself.
    // ===============================
    _adaptTabs() {
        const root = this.tabsRef.el;
        if (!root) {
            if (this.state.tabsExtra.length) this.state.tabsExtra = [];
            return;
        }

        const wraps = [...root.querySelectorAll(":scope > .pt_app_tab_wrap")];
        for (const w of wraps) w.classList.remove("pt_app_tab_wrap--hidden");
        if (!wraps.length) {
            if (this.state.tabsExtra.length) this.state.tabsExtra = [];
            return;
        }

        const availableWidth = root.getBoundingClientRect().width;
        const totalWidth = wraps.reduce((sum, w) => sum + w.getBoundingClientRect().width, 0);

        const tabs = this.currentAppNav?.tabs || [];
        let extra = [];

        if (availableWidth < totalWidth) {
            // Reserve space for the "+" button itself.
            let width = 40;
            for (let i = 0; i < wraps.length; i++) {
                width += wraps[i].getBoundingClientRect().width;
                if (availableWidth < width) {
                    const overflowing = wraps.slice(i);
                    overflowing.forEach((w) => w.classList.add("pt_app_tab_wrap--hidden"));
                    const hiddenIds = new Set(overflowing.map((w) => w.dataset.tabId));
                    extra = tabs.filter((t) => hiddenIds.has(String(t.id)));
                    break;
                }
            }
        }

        const sameLength = extra.length === this.state.tabsExtra.length;
        const sameIds = sameLength && extra.every((t, i) => t.id === this.state.tabsExtra[i]?.id);
        if (!sameIds) {
            this.state.tabsExtra = extra;
            if (!extra.length) this.state.tabsOverflowOpen = false;
        }
    }

    toggleTabsOverflow(ev) {
        ev?.stopPropagation?.();
        const opening = !this.state.tabsOverflowOpen;
        this.state.tabsOverflowOpen = opening;

        if (opening) {
            // Close any open tab dropdown too — only one menu at a time.
            const appId = this.currentAppNav?.app?.id;
            const next = { ...this.state.expanded };
            for (const t of this.currentAppNav?.tabs || []) {
                delete next[this._nodeKey(appId, t.id)];
            }
            this.state.expanded = next;
        }
    }

    closeTabsOverflow() {
        this.state.tabsOverflowOpen = false;
    }

    closeExpanded(appId, nodeId) {
        const key = this._nodeKey(appId, nodeId);
        if (this.state.expanded[key]) {
            this.state.expanded = { ...this.state.expanded, [key]: false };
        }
    }

    // ===============================
    // Top-bar search (opens the full-screen apps drawer, pre-filtered)
    // ===============================
    onTopbarSearchFocus() {
        if (!this.state.drawerOpen) {
            this.state.drawerOpen = true;
        }
        this._expandForSearch();
    }

    onTopbarSearchInput(ev) {
        this.state.treeQuery = ev?.target?.value || "";
        if (!this.state.drawerOpen) {
            this.state.drawerOpen = true;
        }
        this._expandForSearch();
    }

    // ===============================
    // RTL Chevron
    // ===============================
    get isRTL() {
        return document.body.classList.contains("o_rtl");
    }

    getChevronClass(appId, nodeId) {
        if (this.isExpanded(appId, nodeId)) return "fa-chevron-down";
        return this.isRTL ? "fa-chevron-left" : "fa-chevron-right";
    }

    // ===============================
    // Drawer
    // ===============================
    toggleDrawer() {
        this.state.drawerOpen = !this.state.drawerOpen;
        if (this.state.drawerOpen) {
            // Always open on the plain apps grid — submenu navigation for
            // the app you're already in lives in the persistent top-bar
            // tabs now, not a drilled-in view here.
            this._expandForSearch();
        }
    }

    closeDrawer() {
        this.state.drawerOpen = false;
    }

    // ===============================
    // Current-menu sync
    // Odoo 19 uses path-based routing (no #menu_id=... hash fragment), so
    // the only reliable source of "which app/menu am I in" is the menu
    // service itself — Odoo resolves it from the URL/session at boot, and
    // our own nav handlers (toggleApp/onNodeClick) call setCurrentMenu()
    // explicitly since our navbar bypasses Odoo's own click handling.
    // ===============================
    _syncCurrentFromMenuService() {
        let app;
        try {
            app = this.menu.getCurrentApp();
        } catch (e) {
            app = null;
        }
        if (app && !this.state.currentMenuId) {
            this.state.currentMenuId = String(app.id);
        }
    }

    // ===============================
    // Search + Filtering
    // ===============================
    onTreeQueryInput(ev) {
        this.state.treeQuery = ev?.target?.value || "";
        this._expandForSearch();
    }

    clearSearch() {
        this.state.treeQuery = "";
    }

    _filterTree(node, q) {
        if (!node) return null;
        if (!q) return node;

        const qq = q.toLowerCase();
        const name = (node.name || "").toLowerCase();
        const selfMatch = name.includes(qq);

        const children = (node.children || [])
            .map((c) => this._filterTree(c, q))
            .filter(Boolean);

        if (selfMatch || children.length) {
            return { ...node, children: selfMatch ? (node.children || []) : children };
        }
        return null;
    }

    get filteredAppsTree() {
        const q = (this.state.treeQuery || "").trim();
        const apps = Array.isArray(this.state.apps) ? this.state.apps : [];
        const trees = this.state.appTrees || {};

        const out = [];
        for (const app of apps) {
            const appId = String(app.id);
            const tree = trees[appId] || null;

            // Hide app only if it has no children AND no action of its own
            if (!tree) continue;
            if (!tree.children.length && !tree.action) continue;

            if (!q) {
                out.push({ app, tree });
                continue;
            }

            const matchApp = (app.name || "").toLowerCase().includes(q.toLowerCase());
            const filteredTree = this._filterTree(tree, q);

            if (matchApp || filteredTree) {
                out.push({ app, tree: filteredTree || tree });
            }
        }
        return out;
    }

    _expandForSearch() {
        const q = (this.state.treeQuery || "").trim();
        if (!q) return;

        const next = { ...this.state.expanded };
        for (const app of this.state.apps || []) {
            const appId = String(app.id);
            const tree = this.state.appTrees?.[appId];
            if (!tree) continue;

            const keys = this._collectExpandedForQuery(appId, tree, q);
            if (keys.size) {
                next[`app:${appId}`] = true;
                for (const k of keys) next[k] = true;
            }
        }
        this.state.expanded = next;
    }

    _collectExpandedForQuery(appId, node, q) {
        const out = new Set();
        const qq = q.toLowerCase();

        const walk = (n) => {
            const name = (n.name || "").toLowerCase();
            const matched = name.includes(qq);

            let childMatched = false;
            for (const c of (n.children || [])) {
                if (walk(c)) childMatched = true;
            }

            if ((matched || childMatched) && (n.children || []).length) {
                out.add(this._nodeKey(appId, n.id));
            }
            return matched || childMatched;
        };

        for (const c of (node.children || [])) walk(c);
        return out;
    }

    // ===============================
    // Apps + Menus (menu.getAll)
    // ===============================
    _loadApps() {
        try {
            this.state.apps = this.menu.getApps ? this.menu.getApps() : [];
        } catch (e) {
            console.warn("Property Theme: getApps failed", e);
            this.state.apps = [];
        }
        this._buildAppTrees();
    }

    _buildAppTrees() {
        const allMenus = this._getSafeMenusMap();
        const trees = {};

        for (const app of this.state.apps || []) {
            const appId = String(app.id);
            trees[appId] = this._buildFromMap(appId, allMenus);
        }

        this.state.appTrees = trees;

        if (this.state.drawerOpen) {
            this._expandForSearch();
        }
    }

    _getSafeMenusMap() {
        const map = {};
        try {
            if (this.menu.getAll) {
                const all = this.menu.getAll();
                if (all) {
                    Object.values(all).forEach((rec) => {
                        if (!rec || rec.id === undefined || rec.id === null) return;

                        const id = String(rec.id);
                        const name = (rec.name || "").toString().trim();

                        // Odoo 17+: actionID+actionModel, older may have action
                        let action = null;
                        if (rec.actionID && rec.actionID !== false) {
                            action = `${rec.actionModel},${rec.actionID}`;
                        } else if (rec.action) {
                            // sometimes: "ir.actions.act_window,85"
                            action = String(rec.action);
                        }

                        const childIds = (rec.children || []).map((c) => String(c));
                        map[id] = { id, name, action, childIds };
                    });
                }
            }
        } catch (e) {
            console.warn("Property Theme: getAll failed", e);
        }
        return map;
    }

    _buildFromMap(appId, map) {
        const buildNode = (id, depth) => {
            if (depth > 20) return null;
            const rec = map?.[String(id)];
            if (!rec || !rec.name) return null;

            const children = (rec.childIds || [])
                .map((cid) => buildNode(cid, depth + 1))
                .filter(Boolean);

            if (!rec.action && children.length === 0) return null;

            return { id: String(rec.id), name: rec.name, action: rec.action, children };
        };
        return buildNode(appId, 0);
    }

    _nodeKey(appId, nodeId) {
        return `${String(appId)}:${String(nodeId)}`;
    }

    isExpanded(appId, nodeId) {
        return !!this.state.expanded[this._nodeKey(appId, nodeId)];
    }

    async toggleApp(ev) {
        const appId = String(ev.currentTarget?.dataset?.appId || "");
        if (!appId) return;

        const tree = this.state.appTrees?.[appId];
        // Odoo resolves every app's action server-side (its own, or its
        // first descendant's if it has none), so clicking a tile always
        // navigates straight into the app — same as Enterprise's home
        // menu. Sub-navigation then happens via the persistent top-bar
        // tabs, not a secondary drill-in list here.
        if (tree?.action) {
            this.closeDrawer();
            this.state.currentMenuId = appId;
            try {
                // menu.selectMenu is Odoo's own navigation entrypoint (used
                // by its real navbar) — it resolves the app's action,
                // clears stale breadcrumbs from whatever view we were in,
                // and updates the menu service once the new view is ready.
                await this.menu.selectMenu(Number(appId));
            } catch (e) {
                console.warn("Property Theme: selectMenu (root app) failed", appId, e);
            }
            return;
        }

        // Rare fallback: an app with no resolvable action at all (a pure
        // grouping menu) — expand it in place so its children are reachable.
        const key = `app:${appId}`;
        this.state.expanded = { ...this.state.expanded, [key]: !this.state.expanded[key] };
    }

    toggleNode(ev) {
        ev?.stopPropagation?.();
        const appId = String(ev.currentTarget?.dataset?.appId || "");
        const nodeId = String(ev.currentTarget?.dataset?.nodeId || "");
        if (!appId || !nodeId) return;

        const key = this._nodeKey(appId, nodeId);
        this.state.expanded = { ...this.state.expanded, [key]: !this.state.expanded[key] };
    }

    async onNodeClick(ev) {
        const appId = String(ev.currentTarget?.dataset?.appId || "");
        const nodeId = String(ev.currentTarget?.dataset?.nodeId || "");
        if (!appId || !nodeId) return;

        const tree = this.state.appTrees?.[appId];
        const node = this._findNode(tree, nodeId);
        if (!node) return;

        if (node.action) {
            this.closeDrawer();
            this.state.currentMenuId = nodeId;
            try {
                await this.menu.selectMenu(Number(nodeId));
            } catch (e) {
                console.warn("Property Theme: selectMenu failed", nodeId, e);
            }
        } else {
            const key = this._nodeKey(appId, nodeId);
            this.state.expanded = { ...this.state.expanded, [key]: !this.state.expanded[key] };
        }
    }

    // Top-level tab bar only: a tab with children always opens its dropdown,
    // even if it also has its own action — same rule Odoo's real navbar
    // uses (a section with sub-items is a dropdown trigger, never a direct
    // link). Tabs with no children fall through to the normal navigate
    // behavior in onNodeClick.
    onTabClick(ev) {
        const appId = String(ev.currentTarget?.dataset?.appId || "");
        const nodeId = String(ev.currentTarget?.dataset?.nodeId || "");
        if (!appId || !nodeId) return;

        const tree = this.state.appTrees?.[appId];
        const node = this._findNode(tree, nodeId);
        if (!node) return;

        if (node.children && node.children.length) {
            const key = this._nodeKey(appId, nodeId);
            const opening = !this.state.expanded[key];

            // Only one top-level tab dropdown open at a time — close every
            // other tab's own toggle (their nested sub-expansions, which use
            // different keys, are left untouched).
            const next = { ...this.state.expanded };
            for (const t of this.currentAppNav?.tabs || []) {
                delete next[this._nodeKey(appId, t.id)];
            }
            if (opening) {
                next[key] = true;
                this.state.tabsOverflowOpen = false;
            }
            this.state.expanded = next;
            return;
        }

        this.onNodeClick(ev);
    }

    _findNode(node, id) {
        if (!node) return null;
        if (String(node.id) === String(id)) return node;
        for (const c of node.children || []) {
            const r = this._findNode(c, id);
            if (r) return r;
        }
        return null;
    }

    // ===============================
    // Template Helpers
    // ===============================
    isAppExpanded(appId) {
        const key = `app:${String(appId)}`;
        return !!this.state.expanded[key];
    }

    isActiveMenu(nodeId, currentMenuId) {
        return String(nodeId) === String(currentMenuId);
    }

    isNodeExpanded(appId, nodeId) {
        return this.isExpanded(appId, nodeId);
    }

    // ===============================
    // Apps Grid (Enterprise-style home menu)
    // ===============================
    get expandedApp() {
        const apps = Array.isArray(this.state.apps) ? this.state.apps : [];
        const trees = this.state.appTrees || {};
        for (const app of apps) {
            const appId = String(app.id);
            if (this.state.expanded[`app:${appId}`]) {
                const tree = trees[appId];
                if (tree) return { app, tree };
            }
        }
        return null;
    }

    backToApps() {
        const next = { ...this.state.expanded };
        for (const k of Object.keys(next)) {
            if (k.startsWith("app:")) delete next[k];
        }
        this.state.expanded = next;
    }

    _hashStr(str) {
        let h = 0;
        for (let i = 0; i < str.length; i++) {
            h = (h * 31 + str.charCodeAt(i)) >>> 0;
        }
        return h;
    }

    appTileGradient(name) {
        const palette = [
            "linear-gradient(135deg,#6D299A,#8B3FC4)",
            "linear-gradient(135deg,#01B59A,#02D9BB)",
            "linear-gradient(135deg,#2563EB,#3B82F6)",
            "linear-gradient(135deg,#DB2777,#EC4899)",
            "linear-gradient(135deg,#D97706,#F59E0B)",
            "linear-gradient(135deg,#059669,#10B981)",
            "linear-gradient(135deg,#4F46E5,#6366F1)",
            "linear-gradient(135deg,#DC2626,#EF4444)",
        ];
        const idx = this._hashStr(String(name || "")) % palette.length;
        return palette[idx];
    }

    appTileInitial(name) {
        const s = String(name || "").trim();
        return s ? s[0].toUpperCase() : "؟";
    }

    // Odoo sends webIcon as a raw "iconClass,color,backgroundColor" string
    // only when the app has no icon *file* (module/path form is already
    // resolved server-side into webIconData). Parse it for the FA fallback.
    appIconMeta(app) {
        const raw = app && app.webIcon;
        if (!raw || typeof raw !== "string") return null;
        const parts = raw.split(",");
        if (parts.length !== 3) return null;
        const [iconClass, color, backgroundColor] = parts;
        return { iconClass, color, backgroundColor };
    }

    // ===============================
    // User Menu Actions
    // ===============================
    toggleTopbarUserMenu(ev) {
        ev?.stopPropagation?.();
        this.state.topbarUserMenuOpen = !this.state.topbarUserMenuOpen;
    }

    closeTopbarUserMenu() {
        this.state.topbarUserMenuOpen = false;
    }

    async doLogout() {
        this.closeDrawer();
        this.closeTopbarUserMenu();
        try {
            await this.action.doAction("logout");
        } catch (e) {
            window.location.href = "/web/session/logout";
        }
    }

    async openMyProfile() {
        this.closeDrawer();
        this.closeTopbarUserMenu();
        const uid = this.uid;
        if (!uid) return;

        try {
            // الطريقة الأولى: action رسمي من Odoo لفتح ملف المستخدم
            await this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "res.users",
                res_id: uid,
                views: [[false, "form"]],
                target: "current",
                context: { create: false },
            });
        } catch (e) {
            // الطريقة الاحتياطية: استخدام XML ID
            try {
                await this.action.doAction("base.action_res_users_my");
            } catch (e2) {
                try {
                    await this.action.doAction({
                        type: "ir.actions.act_window",
                        res_model: "res.users",
                        res_id: uid,
                        views: [[false, "form"]],
                        target: "new",
                    });
                } catch (e3) {
                    console.warn("Profile open failed", e3);
                }
            }
        }
    }

    async openActivities() {
        this.closeDrawer();
        this.closeTopbarUserMenu();
        try {
            await this.action.doAction("mail.action_discuss");
        } catch (e) {
            console.warn("Activities open failed", e);
        }
    }

    async openSettings() {
        // currently same as profile in your original code
        return this.openMyProfile();
    }

    // If your XML has this button, keep this method to avoid crashes
    openDefaultAppsMenu() {
        this.closeDrawer();
    }

    static template = "eds_smart_theme.GlobalTopbar";
    static props = {};
}

registry.category("main_components").add("eds_property_theme_global_topbar", {
    Component: PtGlobalTopbar,
});