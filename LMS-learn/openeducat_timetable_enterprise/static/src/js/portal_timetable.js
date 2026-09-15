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

const PortalTimeTableWidget = publicWidget.Widget.extend({
    selector: ".timetable_schedule_portal",

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

        const loadScript = (url) => new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = url;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });

        try {
            await loadScript(`${baseMessages}${language}.min.js`);
        } catch {
            // Use Kendo default messages.
        }
        try {
            await loadScript(`${baseCultures}${language}.min.js`);
            window.kendo?.culture(language);
        } catch {
            // Use Kendo default culture.
        }
        await this.initKendo();
    },

    async initKendo() {
        const container = this.el.querySelector("#timetable_portal_kendo");
        if (!container || !window.kendo || !window.jQuery) {
            return;
        }

        const studentNode = document.querySelector(".stud_id_timetable_parent");
        const studentId = studentNode?.id || false;
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const data = await rpc("/get-timetable/data", {
            stud_id: studentId,
            current_timezone: timezone,
        });

        const kendoData = new window.kendo.data.SchedulerDataSource({
            data: data || [],
        });

        window.jQuery(container).kendoScheduler({
            date: new Date(),
            editable: {
                confirmation: false,
                create: false,
                destroy: false,
                move: false,
                editRecurringMode: "series",
                resize: false,
                template: window.jQuery("#editor").html(),
            },
            majorTimeHeaderTemplate: window.kendo.template(
                "<strong>#=kendo.toString(date, 'HH:mm')#</strong>"
            ),
            edit(event) {
                event.container.find(".k-scheduler-update").hide();
            },
            views: [
                {
                    type: "day",
                    eventTemplate: window.jQuery("#event-template").html(),
                    dateHeaderTemplate: "<span class='k-link k-nav-day'>#=kendo.toString(date, 'ddd dd/M')#</span>",
                },
                {
                    type: "week",
                    selected: true,
                    eventTemplate: window.jQuery("#event-template").html(),
                    dateHeaderTemplate: "<span class='k-link k-nav-day'>#=kendo.toString(date, 'ddd dd/M')#</span>",
                },
                "month",
                {
                    type: "agenda",
                    eventTemplate: window.jQuery("#day-event-template").html(),
                },
            ],
            dataSource: kendoData,
        });
    },
});

publicWidget.registry.PortalTimeTableWidget = PortalTimeTableWidget;
export default PortalTimeTableWidget;
