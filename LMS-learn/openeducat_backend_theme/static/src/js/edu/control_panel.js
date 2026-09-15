/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ControlPanel } from "@web/search/control_panel/control_panel";

patch(ControlPanel.prototype, {
    get openeducatIsMobile() {
        return this.env.isSmall;
    },
});
