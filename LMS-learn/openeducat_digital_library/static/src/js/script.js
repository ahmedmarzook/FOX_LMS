/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Interaction } from "@web/public/interaction";

export class DigitalLibraryFilter extends Interaction {
    static selector = ".digital_library_category";

    dynamicContent = {
        ".select_filter_menu": {
            "t-on-click": (event) => this.selectFilter(event, "material_filter_by"),
        },
        ".select_material_type_menu": {
            "t-on-click": (event) => this.selectFilter(event, "material_type_filter_by"),
        },
        "#search_bar_material_": {
            "t-on-input": (event) => this.filterMaterials(event),
        },
    };

    start() {
        this.el.querySelector(".category_all_li")?.click();
    }

    selectFilter(event, targetId) {
        event.preventDefault();
        const target = this.el.querySelector(`#${targetId}`);
        if (target) {
            const value = event.currentTarget.textContent.trim();
            target.value = value.toLowerCase();
            target.textContent = value;
        }
        this.filterMaterials({
            currentTarget: this.el.querySelector("#search_bar_material_"),
        });
    }

    filterMaterials(event) {
        const query = String(event.currentTarget?.value || "").trim().toUpperCase();
        for (const item of this.el.querySelectorAll(".search_filter_div")) {
            const name = String(item.dataset.name || "").toUpperCase();
            item.hidden = !name.includes(query);
        }
    }
}

registry.category("public.interactions").add(
    "openeducat_digital_library.filter",
    DigitalLibraryFilter
);
