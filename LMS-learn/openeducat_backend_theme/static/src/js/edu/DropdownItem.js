/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

patch(DropdownItem.prototype, {
    get openeducatThemeItem() {
        return true;
    },
});
