/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("openeducat_job_detail_tour", {
    steps: () => [
        {
            content: "The published job detail is displayed",
            trigger: "#job_post_field",
        },
    ],
});
