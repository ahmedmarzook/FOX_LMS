/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

const PortalMeetingWidget = publicWidget.Widget.extend({
    selector: ".meeting_schedule_portal",
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
        await this._setLocaleKendo();
    },

    _getFrontendLanguage() {
        const match = document.cookie.match(/(?:^|; )frontend_lang=([^;]*)/);
        const language = match ? decodeURIComponent(match[1]) : document.documentElement.lang;
        return (language || "en-US").replace("_", "-");
    },

    async _setLocaleKendo() {
        const language = this._getFrontendLanguage();
        const messages = `https://kendo.cdn.telerik.com/2021.1.330/js/messages/kendo.messages.${language}.min.js`;
        const cultures = `https://kendo.cdn.telerik.com/2021.1.330/js/cultures/kendo.culture.${language}.min.js`;
        try {
            await Promise.allSettled([$.getScript(messages), $.getScript(cultures)]);
            if (window.kendo) {
                kendo.culture(language);
            }
        } finally {
            await this._initKendo();
        }
    },

    async _initKendo() {
        if (!window.kendo || !this.el.querySelector("#meeting_portal_kendo")) {
            return;
        }
        const studId = this.el.querySelector(".stud_id_meeting_parent")?.id || null;
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const data = await rpc("/get-meeting/data", {
            stud_id: studId,
            current_timezone: timezone,
        });
        const source = new kendo.data.SchedulerDataSource({ data });
        $(this.el).find("#meeting_portal_kendo").kendoScheduler({
            date: new Date(),
            editable: {
                confirmation: false,
                create: false,
                destroy: false,
                move: false,
                editRecurringMode: "series",
                resize: false,
                template: $(this.el).find("#editor").html(),
            },
            majorTimeHeaderTemplate: kendo.template("<strong>#=kendo.toString(date, 'HH:mm')#</strong>"),
            edit(ev) {
                ev.container.find(".k-scheduler-update").hide();
            },
            views: [
                { type: "day", eventTemplate: $(this.el).find("#event-template").html(), dateHeaderTemplate: "<span class='k-link k-nav-day'>#=kendo.toString(date, 'ddd dd/M')#</span>" },
                { type: "week", eventTemplate: $(this.el).find("#event-template").html(), dateHeaderTemplate: "<span class='k-link k-nav-day'>#=kendo.toString(date, 'ddd dd/M')#</span>" },
                { type: "month", eventTemplate: $(this.el).find("#event-template").html() },
                { type: "agenda", selected: true, eventTemplate: $(this.el).find("#day-event-template").html() },
            ],
            dataSource: source,
        });
    },
});

publicWidget.registry.PortalMeetingWidget = PortalMeetingWidget;
