/** @odoo-module **/

import { Component } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class LiveAssignmentSystray extends Component {
    static template = "openeducat_live_assignment.LiveAssignmentSystray";
    static props = ["*"];

    setup() {
        this.action = useService("action");
        this.notification = useService("notification");
    }

    get isDiscussPage() {
        const url = decodeURIComponent(window.location.href);
        return (
            /\/discuss(?:\/|$)/.test(url) ||
            /active_id=discuss\.channel_\d+/.test(url) ||
            /model=discuss\.channel/.test(url)
        );
    }

    get channelId() {
        const url = decodeURIComponent(window.location.href);
        const patterns = [
            /active_id=discuss\.channel_(\d+)/,
            /\/discuss\/channel\/(\d+)/,
            /\/discuss\/(\d+)/,
            /model=discuss\.channel[^#&]*[&#]id=(\d+)/,
        ];
        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match) {
                return Number(match[1]);
            }
        }
        return false;
    }

    async createAssignment() {
        const channelId = this.channelId;
        if (!channelId) {
            this.notification.add(
                "Open a live meeting channel in Discuss first.",
                { type: "warning" }
            );
            return;
        }

        let context;
        try {
            context = await rpc(
                "/openeducat_live_assignment/context",
                { channel_id: channelId }
            );
        } catch (error) {
            console.error("Unable to load live assignment context", error);
            this.notification.add(
                "The live meeting assignment context could not be loaded.",
                { type: "danger" }
            );
            return;
        }

        if (context?.error === "calendar_event_not_found") {
            this.notification.add(
                "This Discuss channel is not linked to a live calendar meeting.",
                { type: "warning" }
            );
            return;
        }
        if (context?.error) {
            this.notification.add(
                "The current live meeting channel could not be found.",
                { type: "warning" }
            );
            return;
        }

        await this.action.doAction({
            name: "Assignment",
            type: "ir.actions.act_window",
            res_model: "op.assignment",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_course_id: context.course || false,
                default_batch_id: context.batch || false,
                default_subject_id: context.subject || false,
            },
        });
    }
}

registry.category("systray").add(
    "openeducat_live_assignment.LiveAssignmentSystray",
    { Component: LiveAssignmentSystray },
    { sequence: 30 }
);
