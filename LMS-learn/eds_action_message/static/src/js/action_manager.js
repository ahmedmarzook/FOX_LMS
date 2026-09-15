/** @odoo-module */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

registry.category("services").add("eds_action_message", {
    dependencies: ["action", "notification", "dialog"],
    start(env, { action: actionService, notification }) {
        const _doAction = actionService.doAction.bind(actionService);

        actionService.doAction = async function (actionRequest, options) {
            const result = await _doAction(actionRequest, options);
            const action = typeof actionRequest === "object" ? actionRequest : {};

            if (action.error_messages) {
                action.error_messages.forEach((message) => {
                    console.warn(message.error);
                    console.log(message.tb);
                });
            }

            if (action.notify && action.message) {
                notification.add(action.message, {
                    title: action.title || _t("Alert"),
                    type: "info",
                    sticky: action.sticky !== false,
                });
            } else if (action.warn && action.message) {
                notification.add(action.message, {
                    title: action.title || _t("Warning"),
                    type: "warning",
                    sticky: action.sticky !== false,
                });
            }

            return result;
        };
    },
});