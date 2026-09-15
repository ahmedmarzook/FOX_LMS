/** @odoo-module **/

import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { onMounted, onWillStart, onWillUnmount, useEffect, useState } from "@odoo/owl";
import { rpc as jsonrpc } from "@web/core/network/rpc";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";
import { useBus, useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";
import { getNavBarDirection, getUiDirection, SMART_UI_DIRECTION_EVENT } from "./ui_direction";

/** sessionStorage: last Odoo URL hash when the user was outside Smart Portal. */
const SMART_PREV_HASH_KEY = "eds_smart_theme.smart_dashboard.prev_non_portal_hash";

patch(NavBar.prototype, {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.notification = useService("notification");
        /** Community-native "home menu" app grid (see static/src/js/home_menu.js). */
        this.hm = useService("eds_smart_theme.home_menu");
        this.shPlaceholderSearch = _t("Search for a service or topic...");
        this.shTitleProfile = _t("Profile");
        this.shLabelMyProfile = _t("My profile");
        this.shLabelPreferences = _t("Preferences");
        this.shLabelLogout = _t("Log out");
        this.shTitleLanguage = _t("Language");
        this.shTitleDashboard = _t("Dashboard");
        this.shTitleMainMenu = _t("القائمة الرئيسية");
        this.shTitleAccessibility = _t("إمكانية الوصول");
        this.shTitleHelpCenter = _t("مركز المساعدة");
        this.shTitleResources = _t("المكتبة الإلكترونية");
        this.shTitleSmartPortal = _t("Smart Portal");
        this.shTitleBackFromPortal = _t("Back to previous page");
        /** Current app: home toggle + section menus (icon dropdown). */
        this.shTitleAppNav = _t("تطبيقي والقوائم");
        this.shTitleNotifications = _t("البلاغات");
        this.shBrandLogoUrl = "/eds_smart_theme/static/src/smart_dashboard/img/logo2.jpeg";
        this.shLabelSeeAll = _t("See all");
        this.shLabelLangSingle = _t("Only one language is available.");
        this.shLabelLangLoadFail = _t("Language list could not be loaded.");
        this.shLabelLangError = _t("Could not change language.");
        this.shLabelSearchUnavailable = _t("Global search is not available on this screen.");
        this.shLabelHelpCenterUnavailable = _t("Help center is not available right now.");

        this.shNotifications = [
            { title: _t("Leave request approved"), sub: _t("10 minutes ago") },
            { title: _t("New task waiting for you"), sub: _t("Today 11:20") },
            { title: _t("Update on HR circular"), sub: _t("Yesterday") },
        ];

        this.shResourcesMenuItems = [

        ];

        this.smartPortalNavSearchFieldId = "smart-portal-nav-search-field";
        this.smartNavState = useState({
            openDd: null,
            langList: [],
            /** True when the enterprise home menu overlay is open. */
            homeMenuOpen: false,
            /** True when the active client action is Smart Portal (`eds_smart_theme_smart_dashboard`). */
            portalLiveSearch: false,
            /** Inverted direction applied to the navbar root so toolbar icons land on the correct visual sides. */
            uiDirection: getNavBarDirection(),
            /** Actual page direction (rtl/ltr) applied to the menus slot so Arabic text flows correctly. */
            pageDirection: getUiDirection(),
            bootstrap: {
                user_name: session.name || "",
                avatar_url: "/web/static/img/user_menu_avatar.png",
                department: "",
            },
        });

        useBus(this.env.bus, "HOME-MENU:TOGGLED", () => {
            this.smartNavState.homeMenuOpen = Boolean(this.hm?.hasHomeMenu);
        });

        this._smartSyncNavDirection = () => {
            this.smartNavState.uiDirection = getNavBarDirection();
            this.smartNavState.pageDirection = getUiDirection();
        };

        this._smartSyncPortalSearchMode = () => {
            const ctrl = this.actionService?.currentController;
            const action = ctrl?.action;
            const next =
                Boolean(action) &&
                action.type === "ir.actions.client" &&
                action.tag === "eds_smart_theme_smart_dashboard";
            this.smartNavState.portalLiveSearch = next;
            document.body.classList.toggle("o_smart_portal_active", next);
            this._smartSyncNavDirection();
            if (next) {
                browser.requestAnimationFrame(() => this._smartSyncNavDirection());
            }
            if (!next) {
                const hash = browser.location.hash || "";
                if (hash.length > 1) {
                    try {
                        browser.sessionStorage.setItem(SMART_PREV_HASH_KEY, hash);
                    } catch {
                        /* private mode / quota */
                    }
                }
            }
        };
        useBus(this.env.bus, "ACTION_MANAGER:UPDATE", this._smartSyncPortalSearchMode);
        useBus(this.env.bus, "ACTION_MANAGER:UI-UPDATED", this._smartSyncPortalSearchMode);

        this._smartOnPortalSearchBound = () => {
            if (!this.smartNavState.portalLiveSearch) {
                return;
            }
            this._smartSyncNavSearchFromGlobal();
        };

        onWillStart(async () => {
            try {
                const data = await jsonrpc("/eds_smart_theme/smart_dashboard/bootstrap", {});
                Object.assign(this.smartNavState.bootstrap, data);
            } catch {
                /* defaults above */
            }
        });

        this._smartOnKey = (ev) => {
            if (ev.key === "Escape") {
                this.smartNavState.openDd = null;
            }
        };
        this._smartDocCloseDds = (ev) => {
            const t = ev?.target;
            if (
                t &&
                typeof t.closest === "function" &&
                t.closest(
                    ".smart-nav-search-slot, .nav-search.search_bar, .nav-search--portal, .search_bar, #search_bar_modal, .top-actions-pill, .topbar__tools, .smart-dd, .dd-wrap"
                )
            ) {
                return;
            }
            this.closeShDds();
        };
        onMounted(() => {
            document.body.classList.add("o_smart_backend");
            document.addEventListener("keydown", this._smartOnKey);
            document.addEventListener("click", this._smartDocCloseDds);
            document.addEventListener("smart-portal-dashboard-search-bound", this._smartOnPortalSearchBound);
            this._smartOnUiDirection = () => {
                this._smartSyncNavDirection();
            };
            document.addEventListener(SMART_UI_DIRECTION_EVENT, this._smartOnUiDirection);
            this._smartSyncPortalSearchMode();
            this.smartNavState.homeMenuOpen = Boolean(this.hm?.hasHomeMenu);
        });
        /* Smart binds $(document).on('click','.search_bar'); OWL + stopPropagation can skip that path.
         * Capture on the navbar root so the search strip always receives a reliable open. */
        useEffect(
            () => {
                const root = this.root?.el;
                const el = root?.querySelector?.(".nav-search.search_bar");
                if (!el) {
                    return () => {};
                }
                const onCap = (ev) => {
                    if (!el.contains(ev.target)) {
                        return;
                    }
                    this.triggerSmartSearch(ev);
                    ev.preventDefault();
                    ev.stopPropagation();
                };
                el.addEventListener("click", onCap, true);
                return () => el.removeEventListener("click", onCap, true);
            },
            () => [this.root?.el, this.smartNavState.portalLiveSearch]
        );
        onWillUnmount(() => {
            document.body.classList.remove("o_smart_backend");
            document.body.classList.remove("o_smart_portal_active");
            document.removeEventListener("keydown", this._smartOnKey);
            document.removeEventListener("click", this._smartDocCloseDds);
            document.removeEventListener("smart-portal-dashboard-search-bound", this._smartOnPortalSearchBound);
            if (this._smartOnUiDirection) {
                document.removeEventListener(SMART_UI_DIRECTION_EVENT, this._smartOnUiDirection);
            }
        });
    },

    _smartSyncNavSearchFromGlobal() {
        const globalSearch = document.getElementById("globalSearch");
        const root = this.root?.el;
        const navIn = root?.querySelector?.(".smart-portal-nav-search");
        if (!globalSearch || !navIn) {
            return;
        }
        navIn.value = globalSearch.value || "";
    },

    onShSmartPortalNavSearchInput(ev) {
        const globalSearch = document.getElementById("globalSearch");
        if (!globalSearch) {
            return;
        }
        const v = ev.target.value;
        if (globalSearch.value !== v) {
            globalSearch.value = v;
        }
        globalSearch.dispatchEvent(new Event("input", { bubbles: true }));
    },

    _smartResolveSearchModal() {
        const root = this.root?.el;
        return (
            root?.querySelector?.("#search_bar_modal") ||
            document.getElementById("search_bar_modal") ||
            null
        );
    },

    _smartSearchModalIsOpen(modal) {
        if (!modal) {
            return false;
        }
        if (modal.classList.contains("show")) {
            return true;
        }
        const $ = window.jQuery;
        if ($) {
            try {
                return $(modal).hasClass("show") || $(modal).css("display") !== "none";
            } catch {
                /* ignore */
            }
        }
        return false;
    },

    /**
     * Open Smart `#search_bar_modal` when its jQuery handler did not change DOM (empty cache, etc.).
     */
    _smartForceOpenSearchModal(modal) {
        const $ = window.jQuery;
        if ($) {
            try {
                const $m = $(modal);
                $m.show();
                $m.addClass("show");
            } catch {
                modal.style.display = "block";
                modal.classList.add("show");
            }
        } else {
            modal.style.display = "block";
            modal.classList.add("show");
        }
        this._all_apps_records_data?.();
        this._searchModalFocus?.();
        const input = modal.querySelector?.("#searchPagesInput");
        if (input) {
            setTimeout(() => input.focus?.(), 120);
        }
    },

    triggerSmartSearch(ev) {
        ev?.preventDefault?.();
        ev?.stopPropagation?.();
        const modal = this._smartResolveSearchModal();
        if (!modal) {
            this.notification.add(this.shLabelSearchUnavailable, { type: "warning" });
            return;
        }
        const wasOpen = this._smartSearchModalIsOpen(modal);
        if (typeof this._showSearchbarModal === "function") {
            try {
                this._showSearchbarModal(ev);
            } catch (err) {
                console.warn("[eds_smart_theme.smart_dashboard] Smart _showSearchbarModal:", err);
            }
        }
        const nowOpen = this._smartSearchModalIsOpen(modal);
        /* Smart often no-ops when $(this.root.el).find('#search_bar_modal') is empty — still return early if it closed an open modal. */
        if (wasOpen && !nowOpen) {
            return;
        }
        if (!wasOpen && !nowOpen) {
            this._smartForceOpenSearchModal(modal);
        }
    },

    onShToggleHomeMenu(ev) {
        ev?.stopPropagation?.();
        this.hm?.toggle?.();
    },

    /** Label / tooltip for the Smart Portal toggle (grid + book toolbar buttons). */
    shAllAppsNavTitle() {
        return this.smartNavState.portalLiveSearch ? this.shTitleBackFromPortal : this.shTitleSmartPortal;
    },

    onShAllApps(ev) {
        ev?.stopPropagation?.();
        if (this.smartNavState.portalLiveSearch) {
            let prev = null;
            try {
                prev = browser.sessionStorage.getItem(SMART_PREV_HASH_KEY);
            } catch {
                prev = null;
            }
            const cur = browser.location.hash || "";
            if (prev && prev.length > 1 && prev !== cur) {
                browser.location.hash = prev;
                return;
            }
            this.hm?.toggle?.();
            return;
        }
        this.actionService.doAction("eds_smart_theme.action_smart_dashboard");
    },

    onShMenuAppsClick(ev) {
        ev?.preventDefault?.();
        this.hm?.toggle?.();
        this.closeShDds();
    },

    async adapt() {
        if (
            !this.smartNavState.portalLiveSearch &&
            this.root?.el?.querySelector?.(".smart-default-nav-menus .o_menu_sections")
        ) {
            return;
        }
        return super.adapt();
    },

    onNavBarDropdownItemSelection(menu) {
        super.onNavBarDropdownItemSelection(menu);
        this.closeShDds();
    },

    onShAccessibility(ev) {
        ev?.stopPropagation?.();
        const main = document.querySelector(".o_web_client .o_action_manager");
        if (main) {
            if (!main.hasAttribute("tabindex")) {
                main.setAttribute("tabindex", "-1");
            }
            main.focus({ preventScroll: false });
        }
    },

    onShResourcesMenuItem(item, ev) {
        ev?.stopPropagation?.();
        this.closeShDds();
        const url = item?.url;
        if (url) {
            browser.open(url, "_blank");
        }
    },

    async onShHelpCenter(ev) {
        ev?.stopPropagation?.();
        try {
            const action = await jsonrpc("/eds_smart_theme/smart_dashboard/help_center_action", {});
            if (action?.type) {
                await this.actionService.doAction(action);
                return;
            }
        } catch {
            /* fall through */
        }
        this.notification.add(this.shLabelHelpCenterUnavailable, { type: "warning" });
    },

    toggleShDd(name, ev) {
        ev.stopPropagation();
        this.smartNavState.openDd = this.smartNavState.openDd === name ? null : name;
    },

    /** Short label for the language pill (e.g. EN, AR). */
    shCurrentLangShort() {
        const lang = session.user_context?.lang || "";
        if (!lang) {
            return "—";
        }
        const base = lang.split("_")[0] || lang;
        return base.length >= 2 ? base.slice(0, 2).toUpperCase() : lang.toUpperCase();
    },

    shLangRowActive(langCode) {
        return langCode === (session.user_context?.lang || "");
    },

    /**
     * Language menu: uses Smart routes /get/active/lang and /change/active/lang (same as systray).
     */
    async toggleShLanguage(ev) {
        ev.stopPropagation();
        if (this.smartNavState.openDd === "language") {
            this.smartNavState.openDd = null;
            return;
        }
        try {
            const list = await jsonrpc("/get/active/lang", {});
            this.smartNavState.langList = Array.isArray(list) ? list : [];
        } catch {
            this.notification.add(this.shLabelLangLoadFail, { type: "warning" });
            return;
        }
        if (this.smartNavState.langList.length <= 1) {
            this.notification.add(this.shLabelLangSingle, { type: "info" });
            return;
        }
        this.smartNavState.openDd = "language";
    },

    async selectShLanguage(langCode) {
        if (!langCode || langCode === session.user_context?.lang) {
            this.closeShDds();
            return;
        }
        try {
            await jsonrpc("/change/active/lang", { lang: langCode });
            await this.actionService.doAction("reload_context");
        } catch {
            this.notification.add(this.shLabelLangError, { type: "danger" });
        }
        this.closeShDds();
    },

    closeShDds() {
        this.smartNavState.openDd = null;
    },

    onShLogout() {
        this.closeShDds();
        window.location.href = "/web/session/logout?redirect=/web/login";
    },

    /**
     * My profile / Preferences: same action as the standard systray User menu
     * (`res.users` form for the current user via `action_get`).
     */
    async onShMyProfile() {
        await this._shOpenUserPreferencesForm();
    },

    async onShPreferences() {
        await this._shOpenUserPreferencesForm();
    },

    async _shOpenUserPreferencesForm() {
        this.closeShDds();
        const actionDescription = await this.env.services.orm.call(
            "res.users",
            "action_get_smart_portal_nav"
        );
        await this.actionService.doAction(actionDescription);
    },

});
