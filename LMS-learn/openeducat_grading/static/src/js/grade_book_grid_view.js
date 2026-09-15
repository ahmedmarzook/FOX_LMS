/** @odoo-module **/

import { Component, onMounted, onWillStart, onWillUnmount, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

function safeParse(value) {
    if (!value) {
        return {};
    }
    if (typeof value === "object") {
        return value;
    }
    try {
        return JSON.parse(value);
    } catch {
        return {};
    }
}

function scalar(value) {
    return value === null || ["string", "number", "boolean"].includes(typeof value);
}

/**
 * Convert the nested gradebook JSON returned by OpenEduCat into a stable,
 * read-only grid.  The original Odoo 16 action used jQuery widgets and
 * AbstractAction; this component uses the Odoo 19 OWL client-action API.
 */
function buildRows(data) {
    const rows = [];
    const walk = (node, path = []) => {
        if (scalar(node)) {
            rows.push({
                level_1: path[0] || "",
                level_2: path[1] || "",
                level_3: path[2] || "",
                level_4: path[3] || "",
                level_5: path[4] || "",
                detail: path.length > 5 ? path.slice(5).join(" / ") : "",
                value: node ?? "",
            });
            return;
        }
        if (Array.isArray(node)) {
            node.forEach((value, index) => walk(value, [...path, String(index + 1)]));
            return;
        }
        for (const [key, value] of Object.entries(node || {})) {
            walk(value, [...path, key]);
        }
    };
    walk(data);
    return rows;
}

class GradeBookGridAction extends Component {
    static template = "openeducat_grading.GradeBookGridAction";
    static actionConfig = {
        model: "gradebook.gradebook",
        method: "get_grade_book_grid_data",
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.gridRef = useRef("grid");
        this.state = useState({ loading: true, empty: false, error: "" });
        this.hot = null;
        this.rawData = {};

        onWillStart(async () => {
            await this.loadData();
        });
        onMounted(() => this.renderGrid());
        onWillUnmount(() => {
            if (this.hot) {
                this.hot.destroy();
                this.hot = null;
            }
        });
    }

    get params() {
        return this.props.action?.params || {};
    }

    async loadData() {
        const config = this.constructor.actionConfig;
        const recordId = Number(this.params.grade_book || 0);
        try {
            let args;
            if (config.model === "gradebook.gradebook") {
                args = [[], recordId, this.params.is_gradebook || false];
            } else {
                args = [[recordId]];
            }
            const result = await this.orm.call(config.model, config.method, args, {});
            this.rawData = safeParse(result?.data ?? result);
            this.state.empty = !Object.keys(this.rawData || {}).length;
        } catch (error) {
            console.error("OpenEduCat gradebook grid failed", error);
            this.state.error = error?.message || _t("Unable to load gradebook data.");
            this.notification.add(this.state.error, { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    renderGrid() {
        if (this.state.loading || this.state.empty || this.state.error || !this.gridRef.el) {
            return;
        }
        if (typeof window.Handsontable === "undefined") {
            this.state.error = _t("Handsontable library could not be loaded.");
            this.notification.add(this.state.error, { type: "danger" });
            return;
        }
        const rows = buildRows(this.rawData);
        this.hot = new window.Handsontable(this.gridRef.el, {
            data: rows,
            columns: [
                { data: "level_1", title: _t("Student / Course"), readOnly: true },
                { data: "level_2", title: _t("Year"), readOnly: true },
                { data: "level_3", title: _t("Term"), readOnly: true },
                { data: "level_4", title: _t("Subject"), readOnly: true },
                { data: "level_5", title: _t("Assignment / Grade"), readOnly: true },
                { data: "detail", title: _t("Detail"), readOnly: true },
                { data: "value", title: _t("Value"), readOnly: true },
            ],
            colHeaders: true,
            rowHeaders: true,
            filters: true,
            dropdownMenu: true,
            columnSorting: true,
            contextMenu: false,
            stretchH: "all",
            height: "auto",
            minSpareRows: 0,
            licenseKey: "non-commercial-and-evaluation",
            className: "htCenter",
        });
    }

    exportCSV() {
        if (!this.hot) {
            return;
        }
        this.hot.getPlugin("exportFile").downloadFile("csv", {
            filename: "GradeBook_[YYYY]-[MM]-[DD]",
            columnHeaders: true,
            rowHeaders: false,
            exportHiddenColumns: true,
            exportHiddenRows: true,
            bom: true,
        });
    }
}

class GradeBookByCourseAction extends GradeBookGridAction {
    static actionConfig = {
        model: "op.course",
        method: "get_grade_book_grid_data_by_course",
    };
}

class GradeBookByBatchAction extends GradeBookGridAction {
    static actionConfig = {
        model: "op.batch",
        method: "get_grade_book_grid_data_by_batch",
    };
}

class GradeBookBySubjectAction extends GradeBookGridAction {
    static actionConfig = {
        model: "op.subject",
        method: "get_grade_book_grid_data_by_subject",
    };
}

class StudentProgressGradeBookAction extends GradeBookGridAction {
    static actionConfig = {
        model: "op.student.progression",
        method: "get_grade_book_grid_data",
    };

    async loadData() {
        const recordId = Number(this.params.grade_book || 0);
        try {
            const result = await this.orm.call(
                "op.student.progression",
                "get_grade_book_grid_data",
                [[recordId]],
                {}
            );
            this.rawData = safeParse(result?.data ?? result);
            this.state.empty = !Object.keys(this.rawData || {}).length;
        } catch (error) {
            console.error("OpenEduCat progression grid failed", error);
            this.state.error = error?.message || _t("Unable to load gradebook data.");
            this.notification.add(this.state.error, { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }
}

const actions = registry.category("actions");
actions.add("grade_book_grade_book_grid", GradeBookGridAction);
actions.add("grade_book_grid_by_course", GradeBookByCourseAction);
actions.add("grade_book_grid_by_batch", GradeBookByBatchAction);
actions.add("grade_book_grid_by_subject", GradeBookBySubjectAction);
actions.add("grade_book_grid", StudentProgressGradeBookAction);
