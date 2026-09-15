/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Interaction } from "@web/public/interaction";

export class MyDigitalLibrary extends Interaction {
    static selector = "#my_digital_library_detail";

    dynamicContent = {
        "#material_detail_search_box": {
            "t-on-input": (event) => this.updateSuggestions(event),
        },
    };

    updateSuggestions(event) {
        const input = event.currentTarget;
        let value = input.value || "";
        const mappings = [
            ["Name Like: ", "name"],
            ["Author Like: ", "author"],
            ["Publisher Like: ", "publisher"],
            ["Tag Like: ", "tag"],
        ];
        for (const [prefix, filter] of mappings) {
            if (value.includes(prefix)) {
                this.el.querySelector("#search_box_filter").value = filter;
                input.value = value.replace(prefix, "");
                this.el.querySelector("#search_box_filter_submit")?.click();
                return;
            }
        }
        const datalist = this.el.querySelector("#search_box_values");
        if (datalist) {
            datalist.replaceChildren(
                ...mappings.map(([prefix, filter]) => {
                    const option = document.createElement("option");
                    option.dataset.filter = filter;
                    option.value = `${prefix}${value}`;
                    return option;
                })
            );
        }
    }
}

registry.category("public.interactions").add(
    "openeducat_digital_library.my_library",
    MyDigitalLibrary
);
