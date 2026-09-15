/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value ?? "";
    return element.innerHTML;
}

function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result || ""));
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(file);
    });
}

function svgDataUrlToPng(dataUrl, imageElement) {
    return new Promise((resolve, reject) => {
        const image = imageElement || new Image();
        image.onload = () => {
            const canvas = document.createElement("canvas");
            canvas.width = image.naturalWidth || image.width;
            canvas.height = image.naturalHeight || image.height;
            canvas.getContext("2d").drawImage(image, 0, 0);
            resolve(canvas.toDataURL("image/png").split(",")[1]);
        };
        image.onerror = reject;
        if (!imageElement) {
            image.src = dataUrl;
        } else if (image.complete) {
            image.onload();
        }
    });
}

class LmsUploadDialog {
    constructor(button) {
        this.button = button;
        this.courseId = Number(button.dataset.channelId || 0);
        this.defaultCategoryId = Number(button.dataset.categoryId || 0);
        this.canUpload = button.dataset.canUpload === "True";
        this.canPublish = button.dataset.canPublish === "True";
        this.modulesToInstall = this.parseModules(button.dataset.modulesToInstall);
        this.installStatus = null;
        this.state = "_select";
        this.file = {};
        this.isValidUrl = true;
        this.sections = [];
        this.tags = [];
        this.modalElement = null;
        this.modal = null;
    }

    parseModules(value) {
        if (!value) {
            return [];
        }
        try {
            return JSON.parse(value.replaceAll("'", '"'));
        } catch {
            return [];
        }
    }

    async open() {
        this.modalElement = document.createElement("div");
        this.modalElement.className = "modal fade";
        this.modalElement.tabIndex = -1;
        this.modalElement.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${escapeHtml(_t("Upload a document"))}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"
                                aria-label="${escapeHtml(_t("Close"))}"></button>
                    </div>
                    <div class="modal-body">
                        <div class="js_alert_container"></div>
                        <div class="o_w_slide_upload_modal_container"></div>
                    </div>
                    <div class="modal-footer"></div>
                </div>
            </div>`;
        document.body.appendChild(this.modalElement);
        this.modal = new bootstrap.Modal(this.modalElement);
        this.modalElement.addEventListener("hidden.bs.modal", () => {
            this.modalElement.remove();
        });
        this.render();
        this.modal.show();
    }

    setState(state) {
        this.state = state;
        this.render();
    }

    render() {
        const container = this.modalElement.querySelector(
            ".o_w_slide_upload_modal_container"
        );
        const title = this.modalElement.querySelector(".modal-title");
        title.textContent =
            this.state === "_import"
                ? _t("New Certification")
                : _t("Upload a document");

        if (this.state === "_select") {
            container.innerHTML = this.renderTypeSelection();
        } else if (this.state === "_upload") {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fa fa-spinner fa-spin fa-3x mb-3"></i>
                    <h4>${escapeHtml(_t("Uploading document ..."))}</h4>
                </div>`;
        } else if (this.state === "_import") {
            const message = this.installStatus?.installing
                ? _t('Installing "%s".', this.installStatus.name)
                : this.installStatus?.failed
                  ? _t('Failed to install "%s".', this.installStatus.name)
                  : _t('Do you want to install the "%s" app?', this.installStatus?.name || "");
            container.innerHTML = `<p id="o_wslides_install_module_text">${escapeHtml(message)}</p>`;
        } else {
            container.innerHTML = this.renderForm();
            this.loadSelectors();
        }

        this.renderButtons();
        this.bindCurrentView();
    }

    renderTypeSelection() {
        const types = [
            ["presentation", "fa-file-pdf-o", _t("Presentation")],
            ["webpage", "fa-file-text", _t("Web Page")],
            ["video", "fa-video-camera", _t("Video")],
            ["quiz", "fa-question-circle", _t("Quiz")],
        ];
        return `
            <div class="row p-1 mt-4">
                ${types.map(([type, icon, label]) => `
                    <div class="col-6 col-md-3">
                        <button type="button"
                                class="content-type d-flex flex-column align-items-center
                                       mb-4 o_wslides_select_type btn rounded border
                                       text-600 p-3 w-100"
                                data-slide-type="${type}">
                            <i class="fa ${icon} mb-2 fa-3x"></i>
                            ${escapeHtml(label)}
                        </button>
                    </div>`).join("")}
            </div>
            ${this.modulesToInstall.map((module) => `
                <button type="button"
                        class="o_wslides_js_upload_install_button w-100 text-center
                               mb-4 btn rounded border text-600 p-3"
                        data-module-id="${Number(module.id)}">
                    <i class="fa fa-trophy"></i>
                    ${escapeHtml(module.motivational || module.name)}
                </button>`).join("")}`;
    }

    renderForm() {
        const fileField =
            this.state === "video" || this.state === "quiz"
                ? ""
                : `
                    <div class="mb-3">
                        <label for="upload" class="form-label">
                            ${escapeHtml(
                                this.state === "webpage"
                                    ? _t("Choose a Cover Image")
                                    : _t("Choose a PDF or an Image")
                            )}
                        </label>
                        <input id="upload" name="file" class="form-control"
                               accept="${this.state === "webpage" ? "image/*" : "image/*,application/pdf"}"
                               type="file" required/>
                    </div>`;

        const urlField =
            this.state === "video"
                ? `
                    <div class="mb-3">
                        <label for="url" class="form-label">${escapeHtml(_t("Youtube Link"))}</label>
                        <input id="url" name="url" class="form-control"
                               placeholder="${escapeHtml(_t("Youtube Video URL"))}"
                               type="url" required/>
                    </div>`
                : "";

        return `
            <form class="needs-validation" novalidate>
                <div class="row">
                    <div id="o_wslides_js_slide_upload_left_column" class="col">
                        ${fileField}
                        ${urlField}
                        <canvas id="data_canvas" class="d-none"></canvas>
                        <div class="mb-3">
                            <label for="name" class="form-label">${escapeHtml(_t("Title"))}</label>
                            <input id="name" name="name" class="form-control" required/>
                        </div>
                        ${this.defaultCategoryId ? "" : `
                            <div class="mb-3">
                                <label for="category_id" class="form-label">${escapeHtml(_t("Section"))}</label>
                                <select id="category_id" class="form-select" required>
                                    <option value="">${escapeHtml(_t("Select Section"))}</option>
                                </select>
                            </div>`}
                        <div class="mb-3">
                            <label for="duration" class="form-label">${escapeHtml(_t("Duration"))}</label>
                            <div class="input-group">
                                <input type="number" id="duration" name="duration"
                                       class="form-control" min="1" value="1" required/>
                                <span class="input-group-text">${escapeHtml(_t("Minutes"))}</span>
                            </div>
                        </div>
                    </div>
                    <div id="o_wslides_js_slide_upload_preview_column"
                         class="col-md-6 d-none">
                        <div class="img-thumbnail">
                            <div class="o_slide_preview">
                                <img src="/openeducat_lms_website/static/src/img/document.png"
                                     id="slide-image" title="${escapeHtml(_t("Content Preview"))}"
                                     alt="${escapeHtml(_t("Content Preview"))}"
                                     class="img-fluid"/>
                            </div>
                        </div>
                    </div>
                </div>
            </form>`;
    }

    renderButtons() {
        const footer = this.modalElement.querySelector(".modal-footer");
        footer.innerHTML = "";

        const addButton = (text, classes, handler, close = false) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = `btn ${classes}`;
            button.textContent = text;
            if (close) {
                button.dataset.bsDismiss = "modal";
            }
            if (handler) {
                button.addEventListener("click", handler);
            }
            footer.appendChild(button);
        };

        if (this.state === "_select") {
            addButton(_t("Cancel"), "btn-secondary", null, true);
            return;
        }

        if (this.state === "_import") {
            if (!this.installStatus?.installing) {
                addButton(
                    this.installStatus?.failed ? _t("Retry") : _t("Install"),
                    "btn-primary",
                    () => this.installModule()
                );
            }
            addButton(_t("Go Back"), "btn-secondary", () => this.goBack());
            return;
        }

        if (this.state === "_upload") {
            return;
        }

        if (this.canUpload) {
            if (this.canPublish) {
                addButton(
                    _t("Publish"),
                    "btn-primary o_w_slide_upload o_w_slide_upload_published",
                    (event) => this.submit(event, true)
                );
                addButton(
                    _t("Save as Draft"),
                    "btn-secondary o_w_slide_upload",
                    (event) => this.submit(event, false)
                );
            } else {
                addButton(
                    _t("Save as Draft"),
                    "btn-primary o_w_slide_upload",
                    (event) => this.submit(event, false)
                );
            }
        }
        addButton(_t("Go Back"), "btn-secondary", () => this.goBack());
    }

    bindCurrentView() {
        this.modalElement
            .querySelectorAll(".o_wslides_select_type")
            .forEach((button) => {
                button.addEventListener("click", () =>
                    this.setState(button.dataset.slideType)
                );
            });

        this.modalElement
            .querySelectorAll(".o_wslides_js_upload_install_button")
            .forEach((button) => {
                button.addEventListener("click", () =>
                    this.selectModule(Number(button.dataset.moduleId))
                );
            });

        this.modalElement
            .querySelector("#upload")
            ?.addEventListener("change", (event) => this.onFileChange(event));

        this.modalElement
            .querySelector("#url")
            ?.addEventListener("change", (event) => this.onUrlChange(event));

        const tags = this.modalElement.querySelector("#tag_ids");
        tags?.addEventListener("keydown", (event) => {
            if (event.key !== "Enter") {
                return;
            }
            event.preventDefault();
            const value = event.target.value?.trim();
            if (!value) {
                return;
            }
            const option = new Option(value, `new:${value}`, true, true);
            tags.add(option);
            event.target.value = "";
        });
    }

    async loadSelectors() {
        try {
            const sectionData = await rpc("/course/section/search_read", {
                fields: ["name"],
                domain: [["course_id", "=", this.courseId]],
            });
            this.sections = sectionData.read_results || [];

            const sectionSelect = this.modalElement.querySelector("#category_id");
            if (sectionSelect) {
                for (const section of this.sections) {
                    sectionSelect.add(new Option(section.name, section.id));
                }
            }
        } catch (error) {
            console.error("Unable to load LMS sections", error);
            this.showAlert(_t("Sections could not be loaded."));
        }
    }

    showAlert(message) {
        const container = this.modalElement.querySelector(".js_alert_container");
        container.innerHTML = `<div class="alert alert-warning" role="alert">${escapeHtml(message)}</div>`;
    }

    clearAlert() {
        this.modalElement.querySelector(".js_alert_container").innerHTML = "";
    }

    showPreview() {
        const left = this.modalElement.querySelector(
            "#o_wslides_js_slide_upload_left_column"
        );
        const preview = this.modalElement.querySelector(
            "#o_wslides_js_slide_upload_preview_column"
        );
        left?.classList.remove("col");
        left?.classList.add("col-md-6");
        preview?.classList.remove("d-none");
        this.modalElement
            .querySelector(".modal-dialog")
            ?.classList.add("modal-lg");
    }

    hidePreview() {
        const left = this.modalElement.querySelector(
            "#o_wslides_js_slide_upload_left_column"
        );
        const preview = this.modalElement.querySelector(
            "#o_wslides_js_slide_upload_preview_column"
        );
        left?.classList.add("col");
        left?.classList.remove("col-md-6");
        preview?.classList.add("d-none");
        this.modalElement
            .querySelector(".modal-dialog")
            ?.classList.remove("modal-lg");
    }

    async onFileChange(event) {
        this.clearAlert();
        const file = event.target.files?.[0];
        if (!file) {
            this.file = {};
            this.hidePreview();
            return;
        }

        const isImage = file.type.startsWith("image/");
        if (!isImage && file.type !== "application/pdf") {
            this.showAlert(_t("Invalid file type. Please select pdf or image file"));
            event.target.value = "";
            this.hidePreview();
            return;
        }

        if (file.size > 25 * 1024 * 1024) {
            this.showAlert(_t("File is too big. File size cannot exceed 25MB"));
            event.target.value = "";
            this.hidePreview();
            return;
        }

        const dataUrl = await readFileAsDataURL(file);
        this.file = {
            name: file.name,
            type: file.type,
            data: dataUrl.split(",")[1],
            dataUrl,
        };

        if (isImage && this.modalElement.querySelector("#slide-image")) {
            this.modalElement.querySelector("#slide-image").src = dataUrl;
        }
        const title = file.name.replace(/\.[^.]+$/, "");
        this.modalElement.querySelector("#name").value = title;
        this.showPreview();
    }

    async onUrlChange(event) {
        this.clearAlert();
        const url = event.target.value.trim();
        this.isValidUrl = false;
        if (!url) {
            return;
        }

        try {
            const data = await rpc("/course/prepare_preview", {
                course_id: this.courseId,
                url,
            });
            if (data.error) {
                this.showAlert(data.error);
                return;
            }

            if (data.total_time) {
                this.modalElement.querySelector("#duration").value = Math.round(
                    data.total_time * 60
                );
            }
            if (data.url_src) {
                this.modalElement.querySelector("#slide-image").src = data.url_src;
            }
            this.modalElement.querySelector("#name").value = data.title || "";
            const description = this.modalElement.querySelector("#description");
            if (description) {
                description.value = data.description || "";
            }
            this.isValidUrl = true;
            this.showPreview();
        } catch (error) {
            console.error("Unable to prepare URL preview", error);
            this.showAlert(_t("Could not fetch data from this URL."));
        }
    }

    getDropdownValues() {
        if (this.defaultCategoryId) {
            return { category_id: [this.defaultCategoryId] };
        }
        return {
            category_id: [
                Number(this.modalElement.querySelector("#category_id").value),
            ],
        };
    }

    async getSubmitValues(publish) {
        const values = {
            course_id: this.courseId,
            name: this.modalElement.querySelector("#name")?.value,
            url: this.modalElement.querySelector("#url")?.value || false,
            description:
                this.modalElement.querySelector("#description")?.value || false,
            duration: this.modalElement.querySelector("#duration")?.value,
            is_published: publish,
            material_type: this.state,
            ...this.getDropdownValues(),
        };

        if (this.file.type === "application/pdf") {
            values.material_type = "document";
            values.mime_type = this.file.type;
            values.datas = this.file.data;
        } else if (this.state === "webpage") {
            values.mime_type = "text/html";
            values.image_1920 =
                this.file.type === "image/svg+xml"
                    ? await svgDataUrlToPng(
                          this.file.dataUrl,
                          this.modalElement.querySelector("#slide-image")
                      )
                    : this.file.data;
        } else if (this.file.type?.startsWith("image/")) {
            if (this.state === "presentation") {
                values.material_type = "infographic";
                values.mime_type =
                    this.file.type === "image/svg+xml"
                        ? "image/png"
                        : this.file.type;
                values.datas =
                    this.file.type === "image/svg+xml"
                        ? await svgDataUrlToPng(
                              this.file.dataUrl,
                              this.modalElement.querySelector("#slide-image")
                          )
                        : this.file.data;
            } else {
                values.image_1920 = this.file.data;
            }
        }

        return values;
    }

    async submit(event, publish) {
        event?.preventDefault();
        const form = this.modalElement.querySelector("form");
        form.classList.add("was-validated");
        if (!form.checkValidity() || !this.isValidUrl) {
            return;
        }

        const previousState = this.state;
        const values = await this.getSubmitValues(publish);
        this.setState("_upload");

        try {
            const result = await rpc("/courses/add_material", values);
            if (result.error) {
                this.setState(previousState);
                this.showAlert(result.error);
                return;
            }
            window.location.assign(result.url);
        } catch (error) {
            console.error("Material upload failed", error);
            this.setState(previousState);
            this.showAlert(_t("The content could not be uploaded."));
        }
    }

    selectModule(moduleId) {
        this.installStatus = {
            ...(this.modulesToInstall.find((module) => Number(module.id) === moduleId) || {}),
        };
        this.setState("_import");
    }

    async installModule() {
        if (!this.installStatus?.id) {
            return;
        }
        this.installStatus.installing = true;
        this.render();
        try {
            await rpc("/web/dataset/call_button", {
                model: "ir.module.module",
                method: "button_immediate_install",
                args: [[Number(this.installStatus.id)]],
                kwargs: {},
            });
            window.location.assign(
                `${window.location.origin}${window.location.pathname}?enable_slide_upload`
            );
        } catch (error) {
            console.error("Module installation failed", error);
            this.installStatus.installing = false;
            this.installStatus.failed = true;
            this.render();
        }
    }

    goBack() {
        this.isValidUrl = true;
        if (this.installStatus && !this.installStatus.installing) {
            this.installStatus = null;
        }
        this.file = {};
        this.setState("_select");
    }
}

function openFromElement(element) {
    return new LmsUploadDialog(element).open();
}

document.addEventListener("click", (event) => {
    const trigger = event.target.closest(".o_wslides_js_slide_upload_lms");
    if (!trigger) {
        return;
    }
    event.preventDefault();
    openFromElement(trigger);
});

document.addEventListener("DOMContentLoaded", () => {
    const trigger = document.querySelector(
        ".o_wslides_js_slide_upload_lms[data-open-modal]"
    );
    if (trigger) {
        trigger.removeAttribute("data-open-modal");
        openFromElement(trigger);
    }
});
