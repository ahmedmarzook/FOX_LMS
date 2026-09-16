/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";
import { renderToElement } from "@web/core/utils/render";

publicWidget.registry.SubjectRegister = publicWidget.Widget.extend({
    selector: ".js_get_data",

    events: {
        "change #course_dropdown": "_onchangedropdown",
    },

    _onchangedropdown: async function (ev) {
        const course_id = $(ev.currentTarget).val();

        try {
            const data = await rpc("/get/course_data", {
                course_id: course_id,
            });

            if (data) {
                const batch_data = renderToElement(
                    "openeducat_core_enterprise.GetBatchData",
                    {
                        batches: data.batch_list,
                    }
                );

                $(".batches").html(batch_data);

                if (data) {
                    const subject_data = renderToElement(
                        "GetSubjectData",
                        {
                            subjects: data.subject_list,
                        }
                    );

                    $(".subjects").html(subject_data);
                }
            }
        } catch (error) {
            console.error("Error loading course data:", error);
        }
    },
});