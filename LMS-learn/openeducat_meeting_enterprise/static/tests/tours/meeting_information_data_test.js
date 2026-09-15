/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("test_meeting_information_data", {
    url: "/meeting/information/data/1/1",
    steps: () => [
        {
            content: "Select Parent Teacher Meeting",
            trigger: "#meeting_name",
        },
    ],
});
