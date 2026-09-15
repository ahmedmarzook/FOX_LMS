/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";

export class ColorPicker extends CharField {
    static template = "openeducat_dashboard_kpi.ColorPicker";

    get color() {
        return String(this.props.value || "#000000,1").split(",")[0];
    }

    get opacity() {
        return String(this.props.value || "#000000,1").split(",")[1] || "1";
    }

    updateColor(event) {
        this.props.update(`${event.target.value},${this.opacity}`);
    }

    updateOpacity(event) {
        this.props.update(`${this.color},${event.target.value}`);
    }
}

registry.category("fields").add("dashboard_pro_color_picker", {
    component: ColorPicker,
    supportedTypes: ["char"],
});
