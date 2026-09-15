/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";

function getChannelId() {
    const url = decodeURIComponent(window.location.href);
    const patterns = [
        /active_id=discuss\.channel_(\d+)/,
        /\/discuss\/channel\/(\d+)/,
        /\/discuss\/(\d+)/,
        /model=discuss\.channel[^#&]*[&#]id=(\d+)/,
    ];
    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match) {
            return Number(match[1]);
        }
    }
    return false;
}

export const attentivenessService = {
    start() {
        let activeLogId = false;
        let busy = false;

        async function startUnfocusedInterval() {
            const channelId = getChannelId();
            if (!channelId || activeLogId || busy) {
                return;
            }
            busy = true;
            try {
                activeLogId = await rpc(
                    "/openeducat_live_attentiveness/start",
                    { channel_id: channelId }
                );
            } catch (error) {
                console.debug("Live attentiveness start was skipped", error);
            } finally {
                busy = false;
            }
        }

        async function endUnfocusedInterval() {
            if (!activeLogId || busy) {
                return;
            }
            busy = true;
            const logId = activeLogId;
            activeLogId = false;
            try {
                await rpc(
                    "/openeducat_live_attentiveness/end",
                    { log_id: logId }
                );
            } catch (error) {
                activeLogId = logId;
                console.debug("Live attentiveness end was skipped", error);
            } finally {
                busy = false;
            }
        }

        function handleVisibility() {
            if (document.hidden || !document.hasFocus()) {
                startUnfocusedInterval();
            } else {
                endUnfocusedInterval();
            }
        }

        document.addEventListener("visibilitychange", handleVisibility);
        window.addEventListener("blur", handleVisibility);
        window.addEventListener("focus", handleVisibility);
        window.addEventListener("beforeunload", () => {
            if (activeLogId) {
                navigator.sendBeacon?.(
                    "/openeducat_live_attentiveness/end",
                    JSON.stringify({
                        jsonrpc: "2.0",
                        method: "call",
                        params: { log_id: activeLogId },
                        id: Date.now(),
                    })
                );
            }
        });

        return {
            getChannelId,
            recordRaisedHand() {
                const channelId = getChannelId();
                return channelId
                    ? rpc("/openeducat_live_attentiveness/raised-hand", {
                          channel_id: channelId,
                      })
                    : false;
            },
        };
    },
};

registry.category("services").add(
    "openeducat_live_attentiveness",
    attentivenessService
);
