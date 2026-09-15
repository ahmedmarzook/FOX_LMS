/** @odoo-module **/

// # Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
// # See LICENSE file for full copyright and licensing details.

import { patch } from "@web/core/utils/patch";
import { SwitchCompanyMenu } from "@web/webclient/switch_company_menu/switch_company_menu";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";

import { UserMenu } from "@web/webclient/user_menu/user_menu";

patch(SwitchCompanyMenu.prototype, {
    setup() {
        super.setup();
        const debugStr = typeof odoo.debug === "string" ? odoo.debug : "";
        this.isDebug = Boolean(debugStr);
        this.isAssets = debugStr.includes("assets");
        this.isTests = debugStr.includes("tests");
    },
});

SwitchCompanyMenu.components = { ...SwitchCompanyMenu.components, UserMenu };

// show company menu even if company is count is 1 
const systrayItemSwitchCompanyMenu = {
    Component: SwitchCompanyMenu,
    isDisplayed() {
        return user.allowedCompanies.length > 0;
    },
};

registry.category("systray").add("SwitchCompanyMenu", systrayItemSwitchCompanyMenu, { sequence: 1, force: true });
registry.category("systray").remove("user_menu");