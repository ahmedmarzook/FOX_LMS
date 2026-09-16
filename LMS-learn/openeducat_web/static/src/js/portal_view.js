```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PortalViewWidget = publicWidget.Widget.extend({
    selector: ".student_portal_view",

    start() {
        this._applyPortalLayout();
        return this._super(...arguments);
    },

    _applyPortalLayout() {
        const portalItems = document.querySelectorAll(
            ".o_portal_docs .list-group-item"
        );

        document.querySelectorAll(".list-group-item").forEach((item) => {
            item.classList.add("dashboard_element_main_body");
        });

        portalItems.forEach((item) => {
            // Prevent wrapping the same element more than once.
            if (item.parentElement?.classList.contains("portal-view-wrapper")) {
                return;
            }

            const wrapper = document.createElement("div");
            wrapper.className =
                "portal-view-wrapper col-12 col-sm-12 col-md-6 col-lg-4 p-2";

            item.parentNode.insertBefore(wrapper, item);
            wrapper.appendChild(item);
        });
    },
});
```
