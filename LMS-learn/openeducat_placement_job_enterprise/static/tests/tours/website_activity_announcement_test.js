/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add('test_website_activity_announcement_apply', {
    url: '/website/activity/announcement',
    steps: () => [
        {
            content: ' go to Activity_detail',
            trigger: 'a[href*=',
        }
    ],
});
