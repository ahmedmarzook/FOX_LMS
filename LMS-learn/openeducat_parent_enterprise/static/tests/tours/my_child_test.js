/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("test_my_child", {
    url: "/my/child/",
    steps: () => [
        {
            content: "Select Sumita S Dani",
            trigger: "h4#child_name:contains('Sumita S Dani')",
        },
    ],
});
