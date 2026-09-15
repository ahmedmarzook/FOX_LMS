/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";

/**
 * Community WebClient opens the first root menu when there is no URL state.
 * Open Smart Portal instead so login lands on the dashboard.
 */
patch(WebClient.prototype, {
    _loadDefaultApp() {
        return this.actionService.doAction("eds_smart_theme.action_smart_dashboard", {
            clearBreadcrumbs: true,
        });
    },
});
