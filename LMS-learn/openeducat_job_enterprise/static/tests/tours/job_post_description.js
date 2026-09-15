/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("openeducat_job_description_tour", {
    steps: () => [
        {
            content: "The job description page is displayed",
            trigger: "#job_post",
        },
    ],
});
