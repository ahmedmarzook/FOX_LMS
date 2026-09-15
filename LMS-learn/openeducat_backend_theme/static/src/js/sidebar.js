/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
import { applyTheme } from "./edu/backend_theme_customizer";

export class OpenEduCatSidebar extends Component {
    static template = "openeducat_backend_theme.Sidebar";
    static props = {};

    setup() {
        this.menu = useService("menu");
        this.state = useState({
            open: false,
            enabled: false,
            query: "",
        });
        onWillStart(async () => {
            const settings = await rpc(
                "/web/backend_theme_customizer/read",
                {}
            );
            applyTheme(settings);
            this.state.enabled =
                settings.company_settings?.theme_menu_style === "sidemenu";
        });
    }

    get apps() {
        const query = this.state.query.trim().toLowerCase();
        const apps = this.menu.getApps();
        return query
            ? apps.filter((app) => app.name.toLowerCase().includes(query))
            : apps;
    }

    toggle() {
        this.state.open = !this.state.open;
    }

    close() {
        this.state.open = false;
    }

    async selectApp(app) {
        await this.menu.selectMenu(app);
        this.close();
    }
}

registry.category("main_components").add(
    "openeducat_backend_theme.Sidebar",
    { Component: OpenEduCatSidebar },
    { sequence: 10 }
);
