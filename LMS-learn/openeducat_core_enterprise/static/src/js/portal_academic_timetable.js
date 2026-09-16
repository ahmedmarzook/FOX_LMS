/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";


publicWidget.registry.PortalAcedamicWidget = publicWidget.Widget.extend({

    selector: ".academic_calendar_portal",

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

    start: async function () {
        await this._super.apply(this, arguments);
        await this.setLocaleKendo();
        return this;
    },

    setLocaleKendo: async function () {

        const self = this;

        // Get current Odoo language
        let language = document.documentElement.lang || "en_US";

        language = language.replace("_", "-");

        const baseUrlMessages =
            "https://kendo.cdn.telerik.com/2021.1.330/js/messages/kendo.messages.";

        const baseUrlCultures =
            "https://kendo.cdn.telerik.com/2021.1.330/js/cultures/kendo.culture.";

        const loadScript = function (url) {
            return new Promise(function (resolve, reject) {
                $.getScript(url)
                    .done(function () {
                        resolve();
                    })
                    .fail(function () {
                        reject();
                    });
            });
        };

        try {

            // Load Kendo language messages
            try {
                await loadScript(
                    baseUrlMessages + language + ".min.js"
                );
            } catch (error) {
                console.warn(
                    "Kendo messages could not be loaded for language:",
                    language
                );
            }

            // Load Kendo culture
            try {
                await loadScript(
                    baseUrlCultures + language + ".min.js"
                );

                if (typeof kendo !== "undefined") {
                    kendo.culture(language);
                }

            } catch (error) {
                console.warn(
                    "Kendo culture could not be loaded for language:",
                    language
                );
            }

        } catch (error) {

            console.error(
                "Error while loading Kendo localization:",
                error
            );

        }

        self.InitKendo();

        return true;
    },

    InitKendo: async function () {

        const self = this;

        const today = new Date();

        const date =
            today.getFullYear() +
            "/" +
            (today.getMonth() + 1) +
            "/" +
            today.getDate();

        const stud_id = $(".stud_id_academic_calendar").attr(
            "current_stud_id"
        );

        const timezone =
            Intl.DateTimeFormat().resolvedOptions().timeZone;

        try {

            const data = await rpc(
                "/get-calendar-event/data",
                {
                    stud_id: stud_id,
                    current_timezone: timezone,
                }
            );

            const kendoData =
                new kendo.data.SchedulerDataSource({
                    data: data,
                });

            $("#academic_calendar_portal_kendo").kendoScheduler({

                date: new Date(date),

                editable: {
                    confirmation: false,
                    create: false,
                    destroy: false,
                    move: false,
                    editRecurringMode: "series",
                    resize: false,
                    template: $("#editor").html(),
                },

                majorTimeHeaderTemplate:
                    kendo.template(
                        "<strong>#=kendo.toString(date, 'HH:mm')#</strong>"
                    ),

                edit: function (e) {
                    e.container
                        .find(".k-scheduler-update")
                        .hide();
                },

                views: [

                    {
                        type: "day",

                        eventTemplate:
                            $("#event-template").html(),

                        dateHeaderTemplate:
                            "<span class='k-link k-nav-day'>" +
                            "#=kendo.toString(date, 'ddd dd/M')#" +
                            "</span>",
                    },

                    {
                        type: "week",

                        selected: true,

                        eventTemplate:
                            $("#event-template").html(),

                        dateHeaderTemplate:
                            "<span class='k-link k-nav-day'>" +
                            "#=kendo.toString(date, 'ddd dd/M')#" +
                            "</span>",
                    },

                    "month",

                    {
                        type: "agenda",

                        eventTemplate:
                            $("#day-event-template").html(),
                    },
                ],

                dataSource: kendoData,
            });

        } catch (error) {

            console.error(
                "Error loading academic calendar data:",
                error
            );

        }
    },
});


return publicWidget.registry.PortalAcedamicWidget;