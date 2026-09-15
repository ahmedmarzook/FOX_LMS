/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { Interaction } from "@web/public/interaction";

export class DigitalMaterialDetail extends Interaction {
    static selector = "#review_course_form";

    dynamicContent = {
        ".description_course_click": {
            "t-on-click": (event) => this.showDescription(event),
        },
        ".review_course_click": {
            "t-on-click": (event) => this.showReviews(event),
        },
        ".star": {
            "t-on-click": (event) => this.selectRating(event),
        },
        "#course_review_submit": {
            "t-on-click": (event) => this.submitReview(event),
        },
        "#material_detail_search_box": {
            "t-on-input": (event) => this.updateSuggestions(event),
        },
    };

    start() {
        this.showReviews();
        this.el.querySelector(".review_success_class")?.classList.add("d-none");
    }

    showDescription(event) {
        event?.preventDefault();
        this.toggleSections(true);
    }

    showReviews(event) {
        event?.preventDefault();
        this.toggleSections(false);
    }

    toggleSections(showDescription) {
        this.el.querySelector(".description_show_class")?.classList.toggle("d-none", !showDescription);
        this.el.querySelector(".review_show_class")?.classList.toggle("d-none", showDescription);
        this.el.querySelector(".review_success_class")?.classList.add("d-none");
        this.el.querySelector(".description_course_click")?.classList.toggle("selected_summary_class", showDescription);
        this.el.querySelector(".review_course_click")?.classList.toggle("selected_summary_class", !showDescription);
    }

    selectRating(event) {
        const rating = this.el.querySelector("#rating_star_val");
        if (rating) {
            rating.value = event.currentTarget.value;
        }
    }

    async submitReview(event) {
        event.preventDefault();
        event.stopPropagation();
        const getValue = (selector) => this.el.querySelector(selector)?.value?.trim() || "";
        const payload = {
            rating: getValue("#rating_star_val"),
            review: getValue("#review_course_review"),
            name: getValue("#review_name_course"),
            email: getValue("#review_email_course"),
            material_id: getValue("#material_id_value"),
        };
        if (!payload.rating || !payload.review || !payload.name || !payload.email || !payload.material_id) {
            window.alert("Please fill in all review fields.");
            return;
        }
        await rpc("/digital-library/add-review", payload);
        this.el.querySelector(".review_show_class")?.classList.add("d-none");
        this.el.querySelector(".review_success_class")?.classList.remove("d-none");
    }

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
    "openeducat_digital_library.material_detail",
    DigitalMaterialDetail
);
