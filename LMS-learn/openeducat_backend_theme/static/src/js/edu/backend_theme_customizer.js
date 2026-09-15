/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";

export function applyTheme(settings) {
    const company = settings.company_settings || {};
    const user = settings.user_settings || {};
    const documentElement = document.documentElement;
    documentElement.style.setProperty(
        "--oe-theme-brand",
        company.theme_color_brand || "#424242"
    );
    documentElement.style.setProperty(
        "--oe-theme-background",
        company.theme_background_color || "#f2f7fb"
    );
    documentElement.style.setProperty(
        "--oe-theme-sidebar",
        company.theme_sidebar_color || "#212529"
    );
    documentElement.style.setProperty(
        "--oe-theme-font",
        company.theme_font_name === "google-font"
            ? company.google_font || "Roboto"
            : company.theme_font_name || "Rubik"
    );
    document.body.classList.toggle("oe_theme_dark", Boolean(user.dark_mode));
    document.body.classList.toggle(
        "oe_theme_chatter_bottom",
        user.chatter_position === "bottom"
    );
    document.body.dataset.themeMenuStyle = company.theme_menu_style || "apps";
}

export class BackendThemeCustomizer extends Component {
    static template = "openeducat_backend_theme.BackendThemeCustomizer";
    static props = {};

    setup() {
        this.notification = useService("notification");
        this.state = useState({
            open: false,
            loading: true,
            saving: false,
            canManageCompany: false,
            user: {
                chatter_position: "sided",
                dark_mode: false,
            },
            company: {
                theme_menu_style: "apps",
                theme_font_name: "Rubik",
                theme_color_brand: "#424242",
                theme_background_color: "#f2f7fb",
                theme_sidebar_color: "#212529",
                google_font: "Roboto",
            },
        });
        onWillStart(() => this.load());
    }

    async load() {
        try {
            const values = await rpc(
                "/web/backend_theme_customizer/read",
                {}
            );
            Object.assign(this.state.user, values.user_settings || {});
            Object.assign(this.state.company, values.company_settings || {});
            this.state.canManageCompany = Boolean(values.can_manage_company);
            applyTheme(values);
        } finally {
            this.state.loading = false;
        }
    }

    toggle() {
        this.state.open = !this.state.open;
    }

    close() {
        this.state.open = false;
    }

    preview() {
        applyTheme({
            user_settings: this.state.user,
            company_settings: this.state.company,
        });
    }

    async save() {
        this.state.saving = true;
        try {
            await rpc("/web/backend_theme_customizer/write", {
                user_settings: { ...this.state.user },
                company_settings: this.state.canManageCompany
                    ? { ...this.state.company }
                    : {},
            });
            this.preview();
            this.notification.add("Theme settings saved.", {
                type: "success",
            });
            this.close();
        } finally {
            this.state.saving = false;
        }
    }
}

registry.category("systray").add(
    "openeducat_backend_theme.customizer",
    { Component: BackendThemeCustomizer },
    { sequence: 5 }
);
