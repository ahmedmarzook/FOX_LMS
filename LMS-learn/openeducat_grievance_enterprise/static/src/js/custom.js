/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";
import { renderToString } from "@web/core/utils/render";

publicWidget.registry.BatchRegisterGrievance =
    publicWidget.Widget.extend({
        selector: ".grievance_portal_form",

        events: {
            "change #course_dropdown": "_onChangeCourse",
            "change #academic_year_dropdown":
                "_onChangeAcademicYear",
            'change select[name="grievance_category_id"]':
                "_onChangeCategory",
            "click .gms-submit-grievance":
                "_onClickSubmit",
        },

        xmlDependencies: [
            "/openeducat_grievance_enterprise/static/src/xml/custom.xml",
        ],

        init: function () {
            this._super.apply(this, arguments);
        },

        async start() {
            await this._super(...arguments);

            this.$(".appeal_grievance_category").prop(
                "disabled",
                true
            );

            await Promise.all([
                this._onChangeCourse(),
                this._onChangeAcademicYear(),
            ]);

            this._onChangeCategory();
        },

        _onClickSubmit: function (event) {
            event.preventDefault();

            const form = this.el.closest("form");

            if (!form) {
                return;
            }

            const input = document.createElement("input");
            input.name = "is_state_change";
            input.type = "hidden";
            input.value = "true";

            form.appendChild(input);

            HTMLFormElement.prototype.submit.call(form);
        },

        async _onChangeCourse() {
            const courseId =
                this.$("#course_dropdown").val();

            if (!courseId) {
                return;
            }

            const data = await rpc(
                "/get/grievance/course_data",
                {
                    course_id: courseId,
                }
            );

            if (!data) {
                return;
            }

            const batchSelect =
                this.$("#batch_on_courses_gms");

            const batchData = renderToString(
                "openeducat_grievance_enterprise.GetBatchData",
                {
                    batches: data.batch_list,
                    selected_id:
                        batchSelect.data("selected") || false,
                }
            );

            batchSelect.html(batchData);
        },

        async _onChangeAcademicYear() {
            const academicYearId =
                this.$("#academic_year_dropdown").val();

            if (!academicYearId) {
                return;
            }

            const data = await rpc(
                "/get/academic_term_data",
                {
                    academic_year_id: academicYearId,
                }
            );

            if (!data) {
                return;
            }

            const termSelect =
                this.$("#term_on_academic_year");

            const academicTermData = renderToString(
                "GetTermData",
                {
                    terms: data.academic_term_list,
                    selected_id:
                        termSelect.data("selected") || false,
                }
            );

            termSelect.html(academicTermData);
        },

        _onChangeCategory: function () {
            const selected = this.$(
                'select[name="grievance_category_id"]'
            ).find("option:selected");

            const isAcademic =
                selected.data("academic") === "academic";

            const academicFields =
                this.$(".non_academic_year");

            academicFields.toggle(isAcademic);

            academicFields.each((index, element) => {
                this._toggleRequired(
                    $(element).find("select, input"),
                    isAcademic
                );
            });
        },

        _toggleRequired: function (elements, state) {
            elements.prop("required", state);
        },
    });