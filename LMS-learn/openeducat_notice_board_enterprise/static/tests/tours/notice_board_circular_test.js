/** @odoo-module **/

import { registry } from "@web/core/registry";

const tourRegistry = registry.category("web_tour.tours");

tourRegistry.add("student_circular_list_view", {
    test: true,
    url: "/my/notice_board/circular/",
    steps: () => [{ content: "select Inter Batch Quiz Competition", trigger: "span:contains(Inter Batch Quiz Competition)" }],
});

tourRegistry.add("parent_circular_list_view", {
    test: true,
    url: "/my/notice_board/circular/1",
    steps: () => [{ content: "select Inter Batch Quiz Competition", trigger: "span:contains(Inter Batch Quiz Competition)" }],
});
