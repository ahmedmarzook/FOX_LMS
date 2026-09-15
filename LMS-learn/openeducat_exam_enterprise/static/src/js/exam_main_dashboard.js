/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ExamMainDashboard extends Component {
    static template = "openeducat_exam_enterprise.ExamMainDashboard";
    static props = ["*"];

    setup() {
        this.action = useService("action");
        this.state = useState({
            loading: true,
            counts: {
                all_exams: 0,
                pending_exams: 0,
                done_exams: 0,
                all_exams_sessions: 0,
            },
            sessions: [],
            selectedSession: 0,
            subjects: [],
            chart: [],
            error: "",
        });
        onWillStart(() => this.loadDashboard());
    }

    async loadDashboard() {
        this.state.loading = true;
        this.state.error = "";
        try {
            const [counts, sessionData, chart] = await Promise.all([
                rpc("/get_exam_counts", {}),
                rpc("/get_exam_sessions", {}),
                rpc("/get_exam_chart_details", {}),
            ]);
            this.state.counts = counts || this.state.counts;
            this.state.sessions = sessionData?.session_ids || [];
            this.state.chart = chart || [];
            this.state.selectedSession = this.state.sessions[0]?.id || 0;
            await this.loadSubjects();
        } catch (error) {
            console.error("Exam dashboard load failed", error);
            this.state.error = error.message || "Unable to load exam dashboard.";
        } finally {
            this.state.loading = false;
        }
    }

    async loadSubjects() {
        if (!this.state.selectedSession) {
            this.state.subjects = [];
            return;
        }
        this.state.subjects = await rpc("/get_subject_details", {
            session_id: this.state.selectedSession,
        });
    }

    async changeSession(event) {
        this.state.selectedSession = Number(event.target.value || 0);
        await this.loadSubjects();
    }

    openExams(state = false) {
        const domain = state ? [["state", "=", state]] : [];
        return this.action.doAction({
            type: "ir.actions.act_window",
            name: "Exams",
            res_model: "op.exam",
            views: [[false, "list"], [false, "form"]],
            domain,
            target: "current",
        });
    }

    openSessions() {
        return this.action.doAction({
            type: "ir.actions.act_window",
            name: "Exam Sessions",
            res_model: "op.exam.session",
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    openExam(exam) {
        return this.action.doAction({
            type: "ir.actions.act_window",
            name: exam.exam,
            res_model: "op.exam",
            res_id: exam.id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    barStyle(item) {
        const maximum = Math.max(...this.state.chart.map((row) => Number(row.ratio || 0)), 1);
        return `height:${Math.max(4, (Number(item.ratio || 0) / maximum) * 100)}%;`;
    }
}

registry.category("actions").add("exam_main_dashboard", ExamMainDashboard);
