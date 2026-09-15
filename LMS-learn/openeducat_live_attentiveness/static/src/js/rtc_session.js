/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * Odoo 19 RTC attentiveness adapter.
 * Browser focus and visibility tracking is handled by the
 * openeducat_live_attentiveness service.
 */
export const rtcAttentivenessAdapter = {
    dependencies: ["openeducat_live_attentiveness"],
    start(env, services) {
        return {
            recordRaisedHand() {
                return services.openeducat_live_attentiveness.recordRaisedHand();
            },
        };
    },
};

registry.category("services").add(
    "openeducat_live_attentiveness_rtc",
    rtcAttentivenessAdapter
);
