/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("openeducat_job_apply_form_tour", {
    steps: () => [
        {
            content: "The application form area is available",
            trigger: "#forms",
        },
    ],
});
