/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value ?? "";
    return element.innerHTML;
}

class CourseSectionDialog {
    constructor(channelId) {
        this.channelId = Number(channelId);
        this.modalElement = null;
        this.modal = null;
    }

    open() {
        this.modalElement = document.createElement("div");
        this.modalElement.className = "modal fade";
        this.modalElement.tabIndex = -1;
        this.modalElement.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${escapeHtml(_t("Add a section"))}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"
                                aria-label="${escapeHtml(_t("Close"))}"></button>
                    </div>
                    <div class="modal-body">
                        <form action="/course/section/add" method="POST"
                              id="course_section_add_form" class="needs-validation" novalidate>
                            <input type="hidden" name="csrf_token"
                                   value="${escapeHtml(odoo.csrf_token || "")}"/>
                            <input type="hidden" name="channel_id"
                                   value="${this.channelId || 0}"/>
                            <div class="mb-3">
                                <label for="sequence" class="form-label">${escapeHtml(_t("Sequence"))}</label>
                                <input type="number" class="form-control" name="sequence"
                                       id="sequence" required/>
                                <div class="invalid-feedback">${escapeHtml(_t("Please fill in this field."))}</div>
                            </div>
                            <div class="mb-3">
                                <label for="section_name" class="form-label">${escapeHtml(_t("Section name"))}</label>
                                <input type="text" class="form-control" name="name"
                                       id="section_name" required/>
                                <div class="invalid-feedback">${escapeHtml(_t("Please fill in this field."))}</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary"
                                data-bs-dismiss="modal">${escapeHtml(_t("Discard"))}</button>
                        <button type="button" class="btn btn-primary js_save_section">
                            ${escapeHtml(_t("Save"))}
                        </button>
                    </div>
                </div>
            </div>`;

        document.body.appendChild(this.modalElement);
        this.modal = new bootstrap.Modal(this.modalElement);
        this.modalElement.querySelector(".js_save_section").addEventListener(
            "click",
            () => this.submit()
        );
        this.modalElement.addEventListener("hidden.bs.modal", () => {
            this.modalElement.remove();
        });
        this.modal.show();
    }

    submit() {
        const form = this.modalElement.querySelector("#course_section_add_form");
        form.classList.add("was-validated");
        if (form.checkValidity()) {
            form.submit();
        }
    }
}

document.addEventListener("click", (event) => {
    const trigger = event.target.closest(".o_wslides_js_slide_section_add");
    if (!trigger) {
        return;
    }
    event.preventDefault();
    const channelId =
        trigger.dataset.channelId ||
        trigger.getAttribute("channel_id");
    new CourseSectionDialog(channelId).open();
});
