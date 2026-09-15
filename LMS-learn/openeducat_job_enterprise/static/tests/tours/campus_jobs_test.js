/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("openeducat_job_list_tour", {
    steps: () => [
        {
            content: "The campus jobs list is displayed",
            trigger: "#job_post_list",
        },
        {
            content: "A published job address is displayed",
            trigger: "#job_post_list #street",
        },
    ],
});
