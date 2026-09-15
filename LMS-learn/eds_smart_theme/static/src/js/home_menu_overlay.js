/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class EdsHomeMenu extends Component {
    static template = "eds_smart_theme.HomeMenu";
    static props = {};

    setup() {
        this.hm = useService("eds_smart_theme.home_menu");
        this.state = useState(this.hm.state);
    }

    get apps() {
        return this.hm.apps;
    }

    onQueryInput(ev) {
        this.hm.state.query = ev.target.value;
    }

    onSelectApp(app) {
        this.hm.selectApp(app);
    }

    close() {
        this.hm.close();
    }

    onKeydown(ev) {
        if (ev.key === "Escape") {
            this.close();
        }
    }
}

registry.category("main_components").add(
    "eds_smart_theme.HomeMenu",
    { Component: EdsHomeMenu },
    { sequence: 15 }
);
