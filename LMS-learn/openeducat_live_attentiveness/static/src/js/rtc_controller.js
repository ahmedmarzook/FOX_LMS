/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class LiveAttentivenessSystray extends Component {
    static template = "openeducat_live_attentiveness.Systray";
    static props = ["*"];

    setup() {
        this.attentiveness = useService("openeducat_live_attentiveness");
        this.notification = useService("notification");
        this.state = useState({ ending: false });
    }

    get visible() {
        return Boolean(this.attentiveness.getChannelId());
    }

    async endMeeting() {
        const channelId = this.attentiveness.getChannelId();
        if (!channelId || this.state.ending) {
            return;
        }
        this.state.ending = true;
        try {
            const result = await rpc(
                "/openeducat_live_attentiveness/end-meeting",
                { channel_id: channelId }
            );
            if (result?.error === "host_required") {
                this.notification.add(
                    "Only the live meeting host can end the meeting.",
                    { type: "warning" }
                );
                return;
            }
            this.notification.add(
                "Live meeting attentiveness report finalized.",
                { type: "success" }
            );
        } finally {
            this.state.ending = false;
        }
    }
}

registry.category("systray").add(
    "openeducat_live_attentiveness.Systray",
    { Component: LiveAttentivenessSystray },
    { sequence: 32 }
);
