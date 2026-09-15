/** @odoo-module **/
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

registry.category("user_menuitems").add(
    "openeducat_theme_settings",
    (env) => ({
        type: "item",
        id: "openeducat_theme_settings",
        description: _t("Theme Settings"),
        callback: () => env.bus.trigger("OPENEDUCAT_THEME:OPEN"),
        sequence: 45,
    })
);
