/** @odoo-module **/

import { Component, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class CreateLiveMeeting extends Component {
    static template = "openeducat_live.CreateLiveMeeting";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        onWillStart(async () => {
            const meetingId =
                this.props.action?.params?.meeting_id ||
                this.props.action?.context?.active_id;
            if (!meetingId) {
                return;
            }
            const action = await this.orm.call(
                "calendar.event",
                "action_create_meet",
                [[meetingId]]
            );
            if (action) {
                await this.action.doAction(action);
            }
        });
    }
}

registry.category("actions").add("create_meet_calendar", CreateLiveMeeting);
