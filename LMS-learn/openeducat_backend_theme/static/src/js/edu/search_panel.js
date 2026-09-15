/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { SearchPanel } from "@web/search/search_panel/search_panel";

patch(SearchPanel.prototype, {
    get openeducatThemeSearchPanel() {
        return true;
    },
});
