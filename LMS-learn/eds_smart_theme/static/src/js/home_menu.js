/** @odoo-module **/
/**
 * Community-native replacement for smart_theme's ent_home_menu.js, which
 * patched Odoo Enterprise's @web_enterprise/webclient/home_menu/home_menu
 * (not available in this Community project). This service+component pair
 * gives backend_nav.js's pre-existing `this.hm?.toggle?.()` hook (in
 * onShToggleHomeMenu) a real full-screen app-grid to open, built the same
 * way openeducat_backend_theme's proven Sidebar (static/src/js/sidebar.js)
 * exposes apps: `useService("menu").getApps()` + `menu.selectMenu(app)`.
 */
import { reactive } from "@odoo/owl";
import { registry } from "@web/core/registry";

export const edsHomeMenuService = {
    dependencies: ["menu"],
    start(env, { menu }) {
        const state = reactive({ open: false, query: "" });
        const service = {
            state,
            get apps() {
                const query = state.query.trim().toLowerCase();
                const apps = menu.getApps();
                return query
                    ? apps.filter((app) => app.name.toLowerCase().includes(query))
                    : apps;
            },
            toggle() {
                state.open = !state.open;
                if (!state.open) {
                    state.query = "";
                }
            },
            open() {
                state.open = true;
            },
            close() {
                state.open = false;
                state.query = "";
            },
            async selectApp(app) {
                await menu.selectMenu(app);
                service.close();
            },
        };
        return service;
    },
};

registry.category("services").add("eds_smart_theme.home_menu", edsHomeMenuService);
