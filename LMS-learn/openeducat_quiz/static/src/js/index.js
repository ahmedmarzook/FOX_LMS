/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";

publicWidget.registry.lms_openeducat_quiz = publicWidget.Widget.extend({
    selector: ".lms_form-horizontal",

    events: {
        "click .quiz_nxt": "_quiz_nxt",
        "click .quiz_prv": "_quiz_prv",
        "click .question_grid_btn": "_question_grid_btn",
        "click .quiz_finish": "_quiz_result_attempt",
    },

    xmlDependencies: [
        "/openeducat_quiz/static/src/xml/question.xml",
    ],

    start: async function () {
        await this._super(...arguments);
        await this._quiz_first_que();
    },

    _call_question_template: function (res) {
        if (!res || !res.next_que || !res.next_que.length) {
            return;
        }

        const nextQuestion = res.next_que[0];
        const nextQuestionId = Number(nextQuestion.id);

        $(".quiz_nxt").val(nextQuestionId);
        $(".quiz_prv").val(nextQuestionId);

        const questionElement = renderToElement("op_quiz_question", {
            res: res.next_que,
            quiz: res.quiz,
            section_name: res.section_name,
        });

        const currentTemplate = document.querySelector("#question_template");
        if (currentTemplate && questionElement) {
            currentTemplate.replaceWith(questionElement);
        }

        if (nextQuestion.last_que) {
            $(".quiz_nxt").addClass("d-none");
            $(".quiz_finish").removeClass("d-none");
        } else {
            $(".quiz_nxt").removeClass("d-none");
            $(".quiz_finish").addClass("d-none");
        }

        if (res.question_no === 1) {
            $(".quiz_prv").addClass("d-none");
        } else {
            $(".quiz_prv").removeClass("d-none");
        }

        this._check_multiple_choice();
    },

    _get_current_answer: function (questionId) {
        const question = $(`.question[value="${questionId}"]`);
        if (!question.length) {
            return undefined;
        }

        const type = question.attr("type");
        if (type === "optional") {
            return question.find(".answer input:checked").val();
        }
        if (type === "blank") {
            return question.find("input[name='answer']").val();
        }
        if (type === "descriptive") {
            return question.find("textarea#descriptive_ans").val();
        }
        if (type === "numeric") {
            return question.find("input#numeric_answer").val();
        }
        return undefined;
    },

    _mark_current_question: function (answer) {
        const currentId = Number($(".question").attr("value"));
        if (!currentId) {
            return;
        }

        const answered =
            $("input[type='radio']:checked").length > 0 ||
            Boolean($("#descriptive_ans").val()) ||
            Boolean(answer);

        $(`.question_grid_btn[value="${currentId}"]`).toggleClass("quiz_req", answered);
        this._check_multiple_choice();
    },

    _check_multiple_choice: function () {
        $('.question[type="multiple_choice"]').each(function () {
            const questionId = $(this).attr("value");
            const gridButton = $(`.question_grid_btn[value="${questionId}"]`);

            const imageSelected = $(this)
                .find(".multiple_choice_image_div.active")
                .length > 0;
            const textSelected = $(this)
                .find(".quiz_multiple_choice_text:checked")
                .length > 0;

            gridButton.toggleClass("quiz_req", imageSelected || textSelected);
        });
    },

    _quiz_nxt: async function () {
        const resultId = Number($("input[name='line_result_id']").val());
        const questionId = Number($(".quiz_nxt").val());
        const answer = this._get_current_answer(questionId);

        try {
            const res = await rpc("/get/quiz-data", {
                result_id: resultId,
                que_id: questionId,
                answer: answer,
            });

            this.que_required = res?.quiz?.que_required;
            this._mark_current_question(answer);
            this._call_question_template(res);
        } catch (error) {
            console.error("OpenEduCat quiz: unable to load next question.", error);
            this.displayNotification({
                message: _t("Unable to load the next question."),
                type: "danger",
            });
        }
    },

    _quiz_prv: async function () {
        const resultId = Number($("input[name='line_result_id']").val());
        const questionId = Number($(".quiz_prv").val());
        const answer = this._get_current_answer(questionId);

        try {
            const res = await rpc("/get/prev-question-data", {
                result_id: resultId,
                que_id: questionId,
                answer: answer,
            });

            this._mark_current_question(answer);
            this._call_question_template(res);
        } catch (error) {
            console.error("OpenEduCat quiz: unable to load previous question.", error);
            this.displayNotification({
                message: _t("Unable to load the previous question."),
                type: "danger",
            });
        }
    },

    _quiz_first_que: async function () {
        const resultId = Number($("input[name='line_result_id']").val());
        const questionId = Number($(".quiz_nxt").val());

        try {
            const res = await rpc("/get/first_que/quiz-data", {
                result_id: resultId,
                que_id: questionId,
            });

            if (res?.state === "submit") {
                $("#result_form").trigger("submit");
                return;
            }

            this.que_required = res?.quiz?.que_required;
            this._call_question_template(res);
        } catch (error) {
            console.error("OpenEduCat quiz: unable to initialize quiz.", error);
            this.displayNotification({
                message: _t("Unable to initialize the quiz."),
                type: "danger",
            });
        }
    },

    _question_grid_btn: async function (event) {
        const resultId = Number($("input[name='line_result_id']").val());
        const questionId = Number($(event.currentTarget).attr("value"));
        const currentQuestionId = Number($(".question").attr("value"));
        const answer = this._get_current_answer(currentQuestionId);

        try {
            const res = await rpc("/get/grid_question_data", {
                result_id: resultId,
                que_id: questionId,
                current_que: currentQuestionId,
                answer: answer,
            });

            this._mark_current_question(answer);
            this._call_question_template(res);
        } catch (error) {
            console.error("OpenEduCat quiz: unable to load selected question.", error);
            this.displayNotification({
                message: _t("Unable to load the selected question."),
                type: "danger",
            });
        }
    },

    _quiz_result_attempt: async function () {
        const resultId = Number($("input[name='line_result_id']").val());
        const currentQuestionId = Number($(".question").attr("value"));
        let unanswered = false;

        this._check_multiple_choice();

        if (this.que_required) {
            $(".question_grid_btn").each(function () {
                if (!$(this).hasClass("quiz_req")) {
                    unanswered = true;
                }
            });
        }

        const answer = this._get_current_answer(currentQuestionId);

        if (unanswered) {
            this.displayNotification({
                message: _t("Answer required"),
                type: "danger",
            });
            return;
        }

        try {
            await rpc("/quiz/attempt-record", {
                result_id: resultId,
                que_id: currentQuestionId,
                answer: answer,
            });
            $("#result_form").trigger("submit");
        } catch (error) {
            console.error("OpenEduCat quiz: unable to save the attempt.", error);
            this.displayNotification({
                message: _t("Unable to save your answer. Please try again."),
                type: "danger",
            });
        }
    },
});

export default publicWidget.registry.lms_openeducat_quiz;
