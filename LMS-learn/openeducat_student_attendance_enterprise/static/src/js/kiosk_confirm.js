/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class StudentAttendanceKioskConfirm extends Component {
    static template = "StudentAttendanceKioskConfirm";

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.notification = useService("notification");
        const params = this.props.action || {};
        this.state = useState({
            studentId: params.student_id,
            studentName: params.student_name || "",
            attendanceSheets: {},
            selectedAttendanceId: false,
            pin: "",
            clock: "",
        });
        onMounted(async () => {
            await this.loadAttendanceSheets();
            this.updateClock();
            this.clockInterval = setInterval(() => this.updateClock(), 500);
        });
        onWillUnmount(() => clearInterval(this.clockInterval));
    }

    get sheetEntries() {
        return Object.entries(this.state.attendanceSheets);
    }

    async loadAttendanceSheets() {
        const result = await this.orm.call(
            "op.student",
            "get_attendance_sheets",
            [this.state.studentId]
        );
        this.state.attendanceSheets = result[0] || {};
        this.state.selectedAttendanceId = result[1]?.is_selected || false;
    }

    updateClock() {
        this.state.clock = new Date().toLocaleTimeString(
            navigator.language,
            { hour: "2-digit", minute: "2-digit", second: "2-digit" }
        );
    }

    addDigit(digit) {
        this.state.pin += String(digit);
    }

    clearPin() {
        this.state.pin = "";
    }

    selectAttendance(event) {
        this.state.selectedAttendanceId = Number(event.target.value);
    }

    async confirm() {
        if (!this.state.selectedAttendanceId) {
            this.notification.add("Please select the attendance sheet.", {
                type: "warning",
            });
            return;
        }
        const result = await this.orm.call(
            "op.student",
            "attendance_manual",
            [[this.state.studentId],
             "openeducat_student_attendance_enterprise.student_attendance_action_kiosk_mode",
             this.state.pin,
             this.state.selectedAttendanceId]
        );
        if (result.action) {
            this.action.doAction(result.action);
        } else if (result.warning) {
            this.notification.add(result.warning, { type: "warning" });
            this.clearPin();
        }
    }

    goBack() {
        this.action.doAction(
            "openeducat_student_attendance_enterprise.student_attendance_action_kiosk_mode",
            { clearBreadcrumbs: true }
        );
    }
}

registry.category("actions").add(
    "student_attendance_kiosk_confirm",
    StudentAttendanceKioskConfirm
);
