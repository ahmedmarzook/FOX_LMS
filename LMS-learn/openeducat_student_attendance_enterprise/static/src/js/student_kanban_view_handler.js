/** @odoo-module **/

import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { patch } from "@web/core/utils/patch";

patch(KanbanRecord.prototype, {
    onGlobalClick(ev) {
        if (
            this.props.record.resModel === "op.student" &&
            ev.target.closest(".o_op_student_attendance_kanban")
        ) {
            this.action.doAction({
                type: "ir.actions.client",
                name: "Confirm",
                tag: "student_attendance_kiosk_confirm",
                student_id: this.props.record.resId,
                student_name: this.props.record.data.name,
            });
            return;
        }
        return super.onGlobalClick(ev);
    },
});
