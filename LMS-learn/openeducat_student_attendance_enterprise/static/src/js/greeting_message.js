/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class StudentAttendanceGreetingMessage extends Component {
    static template = "StudentAttendanceGreetingMessage";

    setup() {
        this.action = useService("action");
        const params = this.props.action || {};
        const attendance = params.attendance || false;
        this.nextAction = params.next_action ||
            "openeducat_student_attendance_enterprise.student_attendance_action_kiosk_mode";
        this.state = useState({
            attendance,
            studentName: params.student_name || "",
            message: attendance ? this.getGreeting(attendance.check_in) : "",
            clock: "",
        });
        onMounted(() => {
            this.updateClock();
            this.clockInterval = setInterval(() => this.updateClock(), 500);
            this.returnTimer = setTimeout(() => this.dismiss(), 5000);
        });
        onWillUnmount(() => {
            clearInterval(this.clockInterval);
            clearTimeout(this.returnTimer);
        });
    }

    getGreeting(checkIn) {
        const hour = checkIn ? new Date(checkIn).getHours() : new Date().getHours();
        if (hour < 5) return _t("Good night");
        if (hour < 12) return _t("Good morning");
        if (hour < 17) return _t("Good afternoon");
        if (hour < 23) return _t("Good evening");
        return _t("Good night");
    }

    updateClock() {
        this.state.clock = new Date().toLocaleTimeString(
            navigator.language,
            { hour: "2-digit", minute: "2-digit", second: "2-digit" }
        );
    }

    dismiss() {
        this.action.doAction(this.nextAction, { clearBreadcrumbs: true });
    }
}

registry.category("actions").add(
    "student_attendance_greeting_message",
    StudentAttendanceGreetingMessage
);
