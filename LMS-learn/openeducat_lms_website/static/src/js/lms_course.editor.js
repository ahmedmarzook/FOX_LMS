/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value ?? "";
    return element.innerHTML;
}

class CourseCreateDialog {
    constructor() {
        this.categories = [];
        this.modalElement = null;
        this.modal = null;
    }

    async open() {
        this.modalElement = document.createElement("div");
        this.modalElement.className = "modal fade";
        this.modalElement.tabIndex = -1;
        this.modalElement.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${escapeHtml(_t("New Course"))}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"
                                aria-label="${escapeHtml(_t("Close"))}"></button>
                    </div>
                    <div class="modal-body">
                        <form action="/lms/course/add" method="POST"
                              id="lms_course_add_form" class="needs-validation" novalidate>
                            <input type="hidden" name="csrf_token"
                                   value="${escapeHtml(odoo.csrf_token || "")}"/>
                            <div class="mb-3">
                                <label for="title" class="form-label">${escapeHtml(_t("Title"))}</label>
                                <input type="text" class="form-control" name="name"
                                       id="title" placeholder="${escapeHtml(_t("Course Title"))}" required/>
                                <div class="invalid-feedback">${escapeHtml(_t("Please fill in this field."))}</div>
                            </div>
                            <div class="mb-3">
                                <label for="code" class="form-label">${escapeHtml(_t("Code"))}</label>
                                <input type="text" class="form-control" name="code"
                                       id="code" required/>
                                <div class="invalid-feedback">${escapeHtml(_t("Please fill in this field."))}</div>
                            </div>
                            <div class="mb-3">
                                <label for="category_ids" class="form-label">${escapeHtml(_t("Category"))}</label>
                                <select class="form-select" id="category_ids" multiple></select>
                                <input type="hidden" name="category_ids" id="category_ids_value"/>
                            </div>
                            <fieldset class="mb-3">
                                <legend class="fs-6">${escapeHtml(_t("Navigation Policy"))}</legend>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio"
                                           name="navigation_policy" id="policy_type1"
                                           value="free_learn" checked/>
                                    <label class="form-check-label" for="policy_type1">
                                        ${escapeHtml(_t("Free Learning Path"))}
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio"
                                           name="navigation_policy" id="policy_type2"
                                           value="seq_learn"/>
                                    <label class="form-check-label" for="policy_type2">
                                        ${escapeHtml(_t("Sequential Learning Path"))}
                                    </label>
                                </div>
                            </fieldset>
                            <div class="mb-3">
                                <label for="description" class="form-label">${escapeHtml(_t("Description"))}</label>
                                <textarea name="short_description" id="description"
                                          class="form-control" rows="5"
                                          placeholder="${escapeHtml(_t("Write here a short description of your first course"))}"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary"
                                data-bs-dismiss="modal">${escapeHtml(_t("Discard"))}</button>
                        <button type="button" class="btn btn-primary js_create_course">
                            ${escapeHtml(_t("Create"))}
                        </button>
                    </div>
                </div>
            </div>`;

        document.body.appendChild(this.modalElement);
        this.modal = new bootstrap.Modal(this.modalElement);
        this.modalElement.addEventListener("hidden.bs.modal", () => {
            this.modalElement.remove();
        });
        this.modalElement
            .querySelector(".js_create_course")
            .addEventListener("click", () => this.submit());

        await this.loadCategories();
        this.modal.show();
    }

    async loadCategories() {
        try {
            const data = await rpc("/lms/category/search_read", {
                fields: ["name"],
                domain: [],
            });
            this.categories = data.read_results || [];
            const select = this.modalElement.querySelector("#category_ids");
            for (const category of this.categories) {
                select.add(new Option(category.name, category.id));
            }
        } catch (error) {
            console.error("Unable to load LMS categories", error);
        }
    }

    submit() {
        const form = this.modalElement.querySelector("#lms_course_add_form");
        form.classList.add("was-validated");
        if (!form.checkValidity()) {
            return;
        }

        const selected = Array.from(
            this.modalElement.querySelector("#category_ids").selectedOptions
        ).map((option) => option.value);
        this.modalElement.querySelector("#category_ids_value").value =
            selected.join(",");
        form.submit();
    }
}

function openCourseCreateDialog() {
    return new CourseCreateDialog().open();
}

document.addEventListener("click", (event) => {
    const trigger = event.target.closest(
        '[data-action="new_lms_course"], [data-name="new_lms_course"], .o_new_lms_course'
    );
    if (!trigger) {
        return;
    }
    event.preventDefault();
    openCourseCreateDialog();
});

window.openeducatCreateLmsCourse = openCourseCreateDialog;
