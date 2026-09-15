/** @odoo-module **/

import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { registry } from "@web/core/registry";

export class Many2ManyAsOne2ManyField extends X2ManyField {

    get isMany2Many() {
        return false;
    }
}

export const many2ManyAsOne2ManyField = {
    ...x2ManyField,
    component: Many2ManyAsOne2ManyField
}

registry.category("fields").add("many2many_as_one2many", many2ManyAsOne2ManyField);