/** @odoo-module **/

import { registry } from "@web/core/registry";

const tourRegistry = registry.category("web_tour.tours");

tourRegistry.add("student_notice_list_view", {
    test: true,
    url: "/my/notice_board/notice/",
    steps: () => [{
        content: "select BOA Student's Misbehaviour in Class",
        trigger: "span:contains(BOA Student's Misbehaviour in Class)",
    }],
});

tourRegistry.add("student_notice_view", {
    test: true,
    url: "/notice_board/notice/1/1",
    steps: () => [{ content: "select Misbehaviour Fine", trigger: "span:contains(Misbehaviour Fine)" }],
});

tourRegistry.add("parent_notice_list_view", {
    test: true,
    url: "/my/notice_board/notice/1",
    steps: () => [{ content: "select BOA Student's Misbehaviour in Class", trigger: "span:contains(BOA Student's Misbehaviour in Class)" }],
});

tourRegistry.add("parent_notice_view", {
    test: true,
    url: "/notice_board/notice/1/1",
    steps: () => [{ content: "select Misbehaviour Fine", trigger: "span:contains(Misbehaviour Fine)" }],
});
