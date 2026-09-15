/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";

/**
 * Odoo 19 compatible renderer wrapper for the onboarding kanban.
 * We keep the standard KanbanRenderer template to avoid fragile template xpaths
 * against Odoo's internal web.KanbanRenderer structure.
 */
export class KanbanRendererOnBoarding extends KanbanRenderer {
    get onboardingTitle() {
        try {
            const records = this.props?.list?.records || [];
            const firstRecord = records[0];
            const plan = firstRecord?.data?.plan_id;
            if (Array.isArray(plan) && plan.length > 1) {
                return plan[1];
            }
        } catch (error) {
            // Keep renderer safe; title is optional.
        }
        return false;
    }
}

registry.category("views").add("no_search_panel_onboarding", {
    ...kanbanView,
    Renderer: KanbanRendererOnBoarding,
    display: {
        ...kanbanView.display,
        controlPanel: false,
    },
});
