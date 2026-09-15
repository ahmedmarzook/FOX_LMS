/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add('test_activity_announcement_apply', {
    url: '/activity/announcement/apply/1',
    steps: () => [
        {
            content: ' go to Activity_detail',
            trigger: 'a[href*=',
        }
    ],
});
