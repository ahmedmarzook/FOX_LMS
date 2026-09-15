/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

const PortalViewWidget = publicWidget.Widget.extend({
    selector: ".parent_tile_portal",

    start() {
        this.el
            .querySelectorAll(".list-group-item")
            .forEach((element) => {
                element.classList.add(
                    "parent_dashboard_element_main_body"
                );
            });
        return this._super(...arguments);
    },
});

publicWidget.registry.PortalViewWidget = PortalViewWidget;

export default PortalViewWidget;
