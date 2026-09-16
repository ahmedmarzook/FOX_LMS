/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

function startQuiz() {
    let quizState = {
        checked_boxes: {},
        blank: {},
        descriptive: {},
        current_que_id: null,
    };

    const configInput = document.querySelector("input[name='config_data']");
    if (!configInput) {
        return;
    }

    const examId = configInput.value;

    rpc("/quiz/configuration", { result_id: examId })
        .then((configureData) => {
            if (configureData.single_que) {
                if (configureData.que_required === 1) {
                    const grid = $(".que_grid");
                    grid.css({
                        "pointer-events": "none",
                        cursor: "default",
                    });
                    $(grid[0]).removeAttr("style");
                }

                const storedQuiz = window.localStorage.getItem("quiz");
                if (storedQuiz) {
                    try {
                        quizState = JSON.parse(storedQuiz) || quizState;
                    } catch {
                        window.localStorage.removeItem("quiz");
                    }
                }

                if (quizState.current_que_id) {
                    changeQuestion(quizState.current_que_id);
                }

                Object.entries(quizState.checked_boxes || {}).forEach(([name, id]) => {
                    const selected = document.getElementById(id);
                    if (selected) {
                        selected.checked = true;
                    }

                    const questionId = $(`input[name="${CSS.escape(name)}"]`)
                        .first()
                        .parent()
                        .attr("index-id");

                    if (questionId) {
                        $(`div[grid-index-id="${CSS.escape(questionId)}"]`).addClass("que_answered");
                    }

                    if (
                        configureData.prev_readonly === 1 &&
                        selected
                    ) {
                        $(`input[name="${CSS.escape(name)}"]`).prop("disabled", true);
                    }

                    if (configureData.que_required === 1 && questionId) {
                        $(`div[grid-index-id="${CSS.escape(questionId)}"]`).removeAttr("style");
                    }
                });

                Object.entries(quizState.blank || {}).forEach(([name, value]) => {
                    $(`input[name="${CSS.escape(name)}"]`).val(value).prop("disabled", true);
                });

                Object.entries(quizState.descriptive || {}).forEach(([name, value]) => {
                    $(`textarea[name="${CSS.escape(name)}"]`).val(value).prop("disabled", true);
                });

                if (quizState.current_que_id !== undefined && quizState.current_que_id !== null) {
                    $(`div[index-id="${CSS.escape(String(quizState.current_que_id))}"]`).addClass("que_show");
                    $(".que_grid").removeClass("que_active");
                    $(`div[grid-index-id="${CSS.escape(String(quizState.current_que_id))}"]`).addClass("que_active");
                } else {
                    $("div[index-id='0']").addClass("que_show");
                    $(".que_grid").removeClass("que_active");
                    $("div[grid-index-id='0']").addClass("que_active");
                }

                if (configureData.prev_allow === 1) {
                    $(".que_grid").css({
                        "pointer-events": "none",
                        cursor: "default",
                    });
                } else {
                    $(".quiz_prv").remove();
                }

                $(document).off("click.openeducatQuizPrev", ".quiz_prv");
                $(document).on("click.openeducatQuizPrev", ".quiz_prv", function () {
                    $("#quiz_err_info").empty();
                    changeQuestion($(this).attr("prev-id"));
                });

                $(".que_grid").off("click.openeducatQuizGrid").on("click.openeducatQuizGrid", function () {
                    const questionId = $(this).attr("grid-index-id");
                    const activeId = $(".que_active").attr("grid-index-id");
                    const radio = $(`div[index-id="${CSS.escape(String(activeId))}"]`).find("input[type='radio']").first();

                    if (radio.length && $(`input[name="${CSS.escape(radio.attr("name"))}"]:checked`).length) {
                        $(`div[grid-index-id="${CSS.escape(String(activeId))}"]`).addClass("que_answered");
                        quizState.checked_boxes[radio.attr("name")] = $(`input[name="${CSS.escape(radio.attr("name"))}"]:checked`).attr("id");
                        quizState.current_que_id = questionId;
                        window.localStorage.setItem("quiz", JSON.stringify(quizState));
                    }

                    $(".que_grid").removeClass("que_active");
                    $(this).addClass("que_active");
                    changeQuestion(questionId);
                    quizState.current_que_id = questionId;
                    window.localStorage.setItem("quiz", JSON.stringify(quizState));
                });
            } else {
                quizState = {
                    checked_boxes: {},
                    blank: {},
                    descriptive: {},
                    current_que_id: null,
                };
                window.localStorage.setItem("quiz", JSON.stringify(quizState));

                $("input[type='radio']").prop("required", configureData.que_required === 1);

                $("input[type='radio']").off("click.openeducatQuiz").on("click.openeducatQuiz", function () {
                    const groupName = $(this).attr("name");

                    if (configureData.prev_readonly === 1) {
                        $(`input[name="${CSS.escape(groupName)}"]`).prop("disabled", true);
                    }

                    quizState.checked_boxes[groupName] = $(this).attr("id");
                    window.localStorage.setItem("quiz", JSON.stringify(quizState));
                });

                $(document).off("click.openeducatQuizFinish", ".quiz_finish");
                $(document).on("click.openeducatQuizFinish", ".quiz_finish", function () {
                    const form = document.querySelector("#from_quiz");

                    if (configureData.que_required === 0 || !form || form.checkValidity()) {
                        if ($("#from_quiz").length) {
                            $("#from_quiz").trigger("submit");
                        } else {
                            $("#from_quiz_dynamic").trigger("submit");
                        }
                    } else {
                        form.reportValidity();
                    }
                });
            }
        })
        .catch((error) => {
            console.error("OpenEduCat quiz configuration error:", error);
            $("#quiz_err_info").html(
                `<div class="alert alert-danger"><strong>${_t("Error")}!</strong> ${_t("Unable to load quiz configuration.")}</div>`
            );
        });

    function changeQuestion(changeId) {
        $("#quiz_err_info").empty();

        const currentId = $(".que_show").attr("index-id");
        if (currentId !== undefined) {
            $(`div[index-id="${CSS.escape(String(currentId))}"]`)
                .addClass("que_hide")
                .removeClass("que_show");
        }

        $(`div[index-id="${CSS.escape(String(changeId))}"]`)
            .addClass("que_show")
            .removeClass("que_hide");

        $(".que_grid").removeClass("que_active");
        $(`div[grid-index-id="${CSS.escape(String(changeId))}"]`).addClass("que_active");

        quizState.current_que_id = Number.parseInt(changeId, 10);
        window.localStorage.setItem("quiz", JSON.stringify(quizState));
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startQuiz, { once: true });
} else {
    startQuiz();
}

export default startQuiz;
