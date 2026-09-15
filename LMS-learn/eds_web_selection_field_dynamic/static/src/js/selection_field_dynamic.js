/** @odoo-module **/
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { SelectionField,selectionField } from "@web/views/fields/selection/selection_field";
import { useSpecialData } from "@web/views/fields/relational_utils";
import { useService } from "@web/core/utils/hooks";
import { evaluateExpr } from "@web/core/py_js/py";

export function tryEvaluateExpr (value, context = {}) {
    if (value === "state") return value;
    try {
        return evaluateExpr(value, context);
    }
    catch {};
    return value;
}

export class SelectionFieldDynamic extends SelectionField {
    static props = {
        ...SelectionField.props,
        selection_model: { type: String, optional: false },
        selection_field: { type: String, optional: false },
    }

    setup() {
        this.type = "selection";
        this.fieldService = useService("field");
        this.specialData = useSpecialData((orm, props) => {
            const selection_model = tryEvaluateExpr(props.selection_model, props.record.evalContext);
            const selection_field = tryEvaluateExpr(props.selection_field, props.record.evalContext);
            if (!selection_model || !selection_field) return null;
            return this.fieldService.loadFields(selection_model, {fieldNames: [selection_field], attributes : ["selection"]})
        });
    }

    get options() {
        const selection_field = tryEvaluateExpr(this.props.selection_field, this.props.record.evalContext);
        const fieldInfo = this.specialData.data?.[selection_field];
        return fieldInfo === undefined ? [] : [...fieldInfo.selection];
    }

    get string() {
        const rawValue = this.props.record.data[this.props.name];
        if (rawValue===false) return "";
        return this.options.find((o) => o[0] === rawValue)[1];
    }

    get value() {
        return this.props.record.data[this.props.name];
    }
}

export const selectionFieldDynamic = {
    ...selectionField,
    component: SelectionFieldDynamic,
    supportedTypes: ["char"],
    extractProps({ attrs, viewType }, dynamicInfo) {
        const props = {
            autosave: viewType === "kanban",
            placeholder: attrs.placeholder,
            required: dynamicInfo.required,
            domain: dynamicInfo.domain(),
            selection_model: attrs.selection_model,
            selection_field: attrs.selection_field,
        };
        if (viewType === "kanban") {
            props.readonly = dynamicInfo.readonly;
        };
        return props;
    },
};

registry.category("fields").add("selection_dynamic", selectionFieldDynamic);
registry.category("fields").add("kanban.selection_dynamic", selectionFieldDynamic);
