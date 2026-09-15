/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

function getCookie(name) {
    const prefix = `${name}=`;
    for (const part of document.cookie.split(";")) {
        const value = part.trim();
        if (value.startsWith(prefix)) {
            return decodeURIComponent(value.slice(prefix.length));
        }
    }
    return "";
}

const PortalOnlineMeetingWidget = publicWidget.Widget.extend({
    selector: ".online_meeting_schedule_portal",

    jsLibs: [
        "/openeducat_web/static/src/kendo_ui/js/jszip.min.js",
        "/openeducat_web/static/src/kendo_ui/js/kendo.all.min.js",
        "/openeducat_web/static/src/kendo_ui/js/kendo.timezones.min.js",
    ],
    cssLibs: [
        "/openeducat_web/static/src/kendo_ui/css/kendo.common.min.css",
        "/openeducat_web/static/src/kendo_ui/css/kendo.default.min.css",
        "/openeducat_web/static/src/kendo_ui/css/kendo.default.mobile.min.css",
    ],

    async start() {
        await this._super(...arguments);
        await this.setLocaleKendo();
    },

    async setLocaleKendo() {
        const frontendLanguage = getCookie("frontend_lang") || document.documentElement.lang || "en_US";
        const language = frontendLanguage.replace("_", "-");
        const baseMessages = "https://kendo.cdn.telerik.com/2021.1.330/js/messages/kendo.messages.";
        const baseCultures = "https://kendo.cdn.telerik.com/2021.1.330/js/cultures/kendo.culture.";

        const loadScript = (url) =>
            new Promise((resolve, reject) => {
                const script = document.createElement("script");
                script.src = url;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });

        try {
            await loadScript(`${baseMessages}${language}.min.js`);
        } catch {
            // Kendo falls back to its default messages.
        }
        try {
            await loadScript(`${baseCultures}${language}.min.js`);
            if (window.kendo) {
                window.kendo.culture(language);
            }
        } catch {
            // Kendo falls back to its default culture.
        }
        await this.initKendo();
    },

    async initKendo() {
        const container = this.el.querySelector("#online_meeting_portal_kendo");
        if (!container || !window.kendo || !window.jQuery) {
            return;
        }

        const studentNode = document.querySelector(".stud_id_online_meeting_parent");
        const studentId = studentNode?.id || false;
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

        const data = await rpc("/get-online-meeting/data", {
            stud_id: studentId,
            current_timezone: timezone,
        });

        const kendoData = new window.kendo.data.SchedulerDataSource({
            data: data || [],
        });

        const today = new Date();
        window.jQuery(container).kendoScheduler({
            date: today,
            editable: {
                confirmation: false,
                create: false,
                destroy: false,
                move: false,
                editRecurringMode: "series",
                resize: false,
                template: window.jQuery("#editor").html(),
            },
            majorTimeHeaderTemplate:
                window.kendo.template("<strong>#=kendo.toString(date, 'HH:mm')#</strong>"),
            edit(ev) {
                ev.container.find(".k-scheduler-update").hide();
            },
            views: [
                {
                    type: "day",
                    eventTemplate: window.jQuery("#event-template").html(),
                    dateHeaderTemplate:
                        "<span class='k-link k-nav-day'>#=kendo.toString(date, 'ddd dd/M')#</span>",
                },
                {
                    type: "week",
                    eventTemplate: window.jQuery("#event-template").html(),
                    dateHeaderTemplate:
                        "<span class='k-link k-nav-day'>#=kendo.toString(date, 'ddd dd/M')#</span>",
                },
                {
                    type: "month",
                    eventTemplate: window.jQuery("#event-template").html(),
                },
                {
                    type: "agenda",
                    selected: true,
                    eventTemplate: window.jQuery("#day-event-template").html(),
                },
            ],
            dataSource: kendoData,
        });
    },
});

publicWidget.registry.PortalOnlineMeetingWidget = PortalOnlineMeetingWidget;
