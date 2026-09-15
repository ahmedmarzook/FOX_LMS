/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add('test_activity_details', {
    url: '/activity/announcement/detail/1',
    steps: () => [
        {
            content: ' go to activity_apply',
            trigger: 'a[href*=',
        }
    ],
});
