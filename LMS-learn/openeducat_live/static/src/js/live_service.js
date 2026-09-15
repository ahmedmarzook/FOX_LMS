/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";

export const liveMeetingService = {
    start() {
        return {
            welcome(channelId, values = {}) {
                return rpc("/openeducat_live/session/welcome", {
                    channel_id: channelId,
                    values,
                });
            },
            checkLock(channelId) {
                return rpc("/openeducat_live/session/check-lock", {
                    channel_id: channelId,
                });
            },
            setMeetingLock(channelId, locked) {
                return rpc("/openeducat_live/session/lock-meeting", {
                    channel_id: channelId,
                    locked,
                });
            },
            setPasswordLock(channelId, locked) {
                return rpc("/openeducat_live/session/lock-password", {
                    channel_id: channelId,
                    locked,
                });
            },
            createPassword(channelId) {
                return rpc("/openeducat_live/session/create-password", {
                    channel_id: channelId,
                });
            },
            updateEmoji(sessionId, emoji) {
                return rpc("/openeducat_live/session/update-emoji", {
                    session_id: sessionId,
                    emoji,
                });
            },
        };
    },
};

registry.category("services").add("openeducat_live", liveMeetingService);
