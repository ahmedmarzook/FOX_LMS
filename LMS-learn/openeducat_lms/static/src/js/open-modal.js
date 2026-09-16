/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

import { rpc } from "@web/core/network/rpc";

import { renderToElement } from "@web/core/utils/render";

publicWidget.registry.OpenModalLms =

    publicWidget.Widget.extend({

        selector: ".card-body",

        events: {

            "click .preview-btn":

                "_onClickPreviewButton",

            "click .edit-btn":

                "_onClickEditButton",

        },

        xmlDependencies: [

            "/openeducat_lms/static/src/xml/openmodal.xml",

        ],

        async _onClickPreviewButton(event) {

            event.preventDefault();

            const materialId = $(

                event.currentTarget

            ).data("material-id");

            if (materialId === undefined) {

                return;

            }

            const data = await rpc(

                "/get/material",

                {

                    material_id: materialId,

                }

            );

            let materialContent = null;

            if (data.embed_code) {

                materialContent =

                    data.embed_code;

            } else if (

                data.material_type === "webpage"

            ) {

                materialContent =

                    data.webpage_content;

            }

            if (!materialContent) {

                return;

            }

            const embedElement =

                renderToElement(

                    "MaterialDetails",

                    {

                        data: materialContent,

                    }

                );

            $(".modal-title-lms").text(

                data.name || ""

            );

            $(".modal-body")

                .empty()

                .append(embedElement);

            if (

                data.material_type === "webpage"

            ) {

                $(".modal-body")

                    .find(".embed-responsive")

                    .removeClass(

                        "embed-responsive"

                    );

            }

            this._showPreviewModal();

        },

        async _onClickEditButton(event) {

            event.preventDefault();

            const materialId = $(

                event.currentTarget

            ).data("material-id");

            if (materialId === undefined) {

                return;

            }

            const data = await rpc(

                "/get/material",

                {

                    material_id: materialId,

                }

            );

            const materialName =

                data.name || "material";

            const slug = encodeURIComponent(

                materialName

                    .trim()

                    .replace(/\s+/g, "-")

            );

            const editUrl = new URL(

                `/material-edit/${slug}-${materialId}`,

                window.location.origin

            );

            editUrl.searchParams.set(

                "fullscreen",

                "0"

            );

            editUrl.searchParams.set(

                "enable_editor",

                "1"

            );

            window.location.href =

                editUrl.toString();

        },

        _showPreviewModal: function () {

            const modalElement =

                document.getElementById(

                    "preview-modal"

                );

            if (!modalElement) {

                return;

            }

            if (

                window.bootstrap &&

                window.bootstrap.Modal

            ) {

                const modal =

                    window.bootstrap.Modal

                        .getOrCreateInstance(

                            modalElement

                        );

                modal.show();

                return;

            }

            /*

             * احتياطي في حالة عدم وجود Bootstrap

             * ككائن عام في الصفحة.

             */

            modalElement.style.display = "block";

            modalElement.classList.add("show");

            modalElement.removeAttribute(

                "aria-hidden"

            );

            modalElement.setAttribute(

                "aria-modal",

                "true"

            );

            modalElement.setAttribute(

                "role",

                "dialog"

            );

            document.body.classList.add(

                "modal-open"

            );

            let backdrop =

                document.querySelector(

                    ".o_lms_modal_backdrop"

                );

            if (!backdrop) {

                backdrop =

                    document.createElement(

                        "div"

                    );

                backdrop.className =

                    "modal-backdrop fade show " +

                    "o_lms_modal_backdrop";

                document.body.appendChild(

                    backdrop

                );

            }

            const closeButtons =

                modalElement.querySelectorAll(

                    '[data-bs-dismiss="modal"],' +

                    '[data-dismiss="modal"],' +

                    ".btn-close," +

                    ".close"

                );

            closeButtons.forEach(

                (button) => {

                    button.addEventListener(

                        "click",

                        () => {

                            this._hidePreviewModal();

                        },

                        {

                            once: true,

                        }

                    );

                }

            );

        },

        _hidePreviewModal: function () {

            const modalElement =

                document.getElementById(

                    "preview-modal"

                );

            if (!modalElement) {

                return;

            }

            modalElement.style.display = "none";

            modalElement.classList.remove("show");

            modalElement.setAttribute(

                "aria-hidden",

                "true"

            );

            modalElement.removeAttribute(

                "aria-modal"

            );

            document.body.classList.remove(

                "modal-open"

            );

            document

                .querySelector(

                    ".o_lms_modal_backdrop"

                )

                ?.remove();

        },

    });