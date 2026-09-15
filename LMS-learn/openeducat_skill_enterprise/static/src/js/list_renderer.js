/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { _t } from "@web/core/l10n/translation";

export class CommonSkillsListRenderer extends ListRenderer {
    get colspan() {
        const span = this.allColumns?.length || this.columns?.length || 1;
        if (this.isEditable) {
            return span + 1;
        }

        return span;
    }

    get groupBy() {
        return "";
    }

    get groupedList() {
        const grouped = {};

        for (const record of this.list.records) {
            const data = record.data;
            const group = data[this.groupBy] || [false, _t("Other")];
            const groupId = Array.isArray(group) ? group[0] : false;
            const groupName = Array.isArray(group) ? group[1] : _t("Other");

            if (grouped[groupName] === undefined) {
                grouped[groupName] = {
                    id: groupId ? parseInt(groupId) : false,
                    name: groupName || _t('Other'),
                    list: {
                        records: [],
                    },
                };
            }

            grouped[groupName].list.records.push(record);
        }
        return grouped;
    }

    get showTable() {
        return this.props.list.records.length;
    }

    get isEditable() {
        return this.props.editable !== false;
    }

    async onCellClicked(record, column, ev) {
        if (!this.isEditable) {
            return;
        }

        return await super.onCellClicked(record, column, ev);
    }
}
CommonSkillsListRenderer.rowsTemplate = "openeducat_skill_enterprise.SkillsListRenderer.Rows";
