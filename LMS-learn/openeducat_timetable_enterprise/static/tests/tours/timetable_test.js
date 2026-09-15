/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("test_timetable", {
    url: "/student/timetable/1",
    steps: () => [
        {
            content: "Select Advanced Taxation",
            trigger: "#subject_name:contains('Advanced Taxation')",
        },
    ],
});
