/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";

patch(NavBar.prototype, {
    get openeducatThemeApps() {
        return this.menuService.getApps();
    },
});
