/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class StudentAttendanceKioskMode extends Component {
    static template = "StudentAttendanceKioskMode";

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.company = useService("company");
        this.state = useState({
            companyName: "",
            companyImageUrl: "",
            clock: "",
        });
        onMounted(() => {
            this.loadCompany();
            this.clockInterval = setInterval(() => this.updateClock(), 500);
            this.updateClock();
        });
        onWillUnmount(() => clearInterval(this.clockInterval));
    }

    async loadCompany() {
        const companyId = this.company.currentCompany.id;
        const companies = await this.orm.read(
            "res.company",
            [companyId],
            ["name"]
        );
        this.state.companyName = companies[0]?.name || "";
        this.state.companyImageUrl =
            `/web/image?model=res.company&id=${companyId}&field=logo`;
    }

    updateClock() {
        this.state.clock = new Date().toLocaleTimeString(
            navigator.language,
            { hour: "2-digit", minute: "2-digit", second: "2-digit" }
        );
    }

    selectStudent() {
        this.action.doAction(
            "openeducat_student_attendance_enterprise.student_attendance_action_kanban"
        );
    }
}

registry.category("actions").add(
    "student_attendance_kiosk_mode",
    StudentAttendanceKioskMode
);
