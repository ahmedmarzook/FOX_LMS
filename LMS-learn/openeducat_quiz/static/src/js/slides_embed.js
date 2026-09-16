/** @odoo-module **/

/*
 * Minimal embedded PDF slide viewer for OpenEduCat.
 *
 * PDFSlidesViewer is intentionally kept as an external dependency because
 * it is supplied by the OpenEduCat/website-slides assets.
 */

function initEmbeddedViewer() {
    const viewerElement = document.querySelector("#PDFViewer");
    const canvas = document.querySelector("#PDFViewerCanvas");

    if (!viewerElement || !canvas || typeof PDFSlidesViewer === "undefined") {
        return;
    }

    const root = $(viewerElement);

    const embeddedViewer = {
        viewer: root,
        slideUrl: root.find("#PDFSlideViewer").data("slideurl"),
        slideId: root.find("#PDFSlideViewer").data("slideid"),
        defaultPage: Number.parseInt(root.find("#PDFSlideViewer").data("defaultpage"), 10) || 1,
        canvas,
        pdfViewer: null,

        find(selector) {
            return this.viewer.find(selector);
        },

        onLoadedFile() {
            this.find("canvas").show();
            this.find("#page_count").text(this.pdfViewer.pdf_page_total);
            this.find("#PDFViewerLoader").hide();

            if (this.pdfViewer.pdf_page_total > 1) {
                this.find(".o_slide_navigation_buttons").removeClass("hide");
            }

            const page = (
                this.defaultPage > 0 &&
                this.defaultPage <= this.pdfViewer.pdf_page_total
            ) ? this.defaultPage : 1;

            this.renderPage(page);
        },

        onRenderedPage(pageNumber) {
            if (pageNumber) {
                this.find("#page_number").val(pageNumber);
            }
        },

        renderPage(pageNumber) {
            return this.pdfViewer
                .renderPage(pageNumber)
                .then((page) => this.onRenderedPage(page));
        },

        changePage() {
            const page = Number.parseInt(this.find("#page_number").val(), 10);

            if (page >= 1 && page <= this.pdfViewer.pdf_page_total) {
                this.pdfViewer.changePage(page).then((pageNumber) => {
                    this.onRenderedPage(pageNumber);
                });
            } else {
                this.find("#page_number").val(this.pdfViewer.pdf_page_current);
            }
        },

        next() {
            this.pdfViewer.nextPage().then((pageNumber) => {
                if (pageNumber) {
                    this.onRenderedPage(pageNumber);
                } else if (this.pdfViewer.pdf) {
                    this.displaySuggestedSlides();
                }
            });
        },

        previous() {
            this.pdfViewer.previousPage().then((pageNumber) => {
                if (pageNumber) {
                    this.onRenderedPage(pageNumber);
                }
                this.find("#slide_suggest").hide();
            });
        },

        first() {
            this.pdfViewer.firstPage().then((pageNumber) => {
                this.onRenderedPage(pageNumber);
                this.find("#slide_suggest").hide();
            });
        },

        last() {
            this.pdfViewer.lastPage().then((pageNumber) => {
                this.onRenderedPage(pageNumber);
                this.find("#slide_suggest").hide();
            });
        },

        fullscreen() {
            this.pdfViewer.toggleFullScreen();
        },

        fullScreenFooter(event) {
            if (event.target.id === "PDFViewerCanvas") {
                this.pdfViewer.toggleFullScreenFooter();
            }
        },

        displaySuggestedSlides() {
            this.find("#slide_suggest").show();
        },
    };

    embeddedViewer.pdfViewer = new PDFSlidesViewer(
        embeddedViewer.slideUrl,
        embeddedViewer.canvas,
        true
    );

    embeddedViewer.pdfViewer.loadDocument().then(() => {
        embeddedViewer.onLoadedFile();
    });

    $("#previous").on("click", () => embeddedViewer.previous());
    $("#next").on("click", () => embeddedViewer.next());
    $("#first").on("click", () => embeddedViewer.first());
    $("#last").on("click", () => embeddedViewer.last());
    $("#page_number").on("change", () => embeddedViewer.changePage());
    $("#fullscreen").on("click", () => embeddedViewer.fullscreen());
    $("#PDFViewer").on("click", (event) => embeddedViewer.fullScreenFooter(event));

    $(document).on("keydown.openeducatSlides", (event) => {
        if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
            embeddedViewer.previous();
        } else if (event.key === "ArrowRight" || event.key === "ArrowDown") {
            embeddedViewer.next();
        }
    });

    $(".oe_slide_js_embed_option_link").on("click", function (event) {
        event.preventDefault();

        const toggleSelector = $(this).data("slide-option-id");
        $(".oe_slide_embed_option").not(toggleSelector).hide();
        $(toggleSelector).slideToggle();
    });

    $(".oe_slides_suggestion_media").hover(
        function () {
            $(this).find(".oe_slides_suggestion_caption").stop(true, true).slideDown(250);
        },
        function () {
            $(this).find(".oe_slides_suggestion_caption").stop(true, true).slideUp(250);
        }
    );

    $(".oe_slide_js_embed_code_widget input").on("change", function () {
        let page = Number.parseInt($(this).val(), 10);

        if (
            !Number.isInteger(page) ||
            page < 1 ||
            page > embeddedViewer.pdfViewer.pdf_page_total
        ) {
            page = 1;
        }

        const input = embeddedViewer.find(".slide_embed_code");
        const actualCode = input.val() || "";
        const newCode = actualCode.replace(
            /(page=).*?([^\d]+)/,
            `$1${page}$2`
        );
        input.val(newCode);
    });

    $(".oe_slide_js_share_email button").on("click", async function () {
        const widget = $(this).closest(".oe_slide_js_share_email");
        const input = widget.find("input");
        const slideId = $(this).data("slide-id");

        if (!input.val() || !input[0].checkValidity()) {
            widget.addClass("has-error");
            input.trigger("focus");
            return;
        }

        widget.removeClass("has-error");

        try {
            await fetch("/slides/slide/send_share_email", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: {
                        slide_id: slideId,
                        email: input.val(),
                    },
                }),
            });

            widget.html(
                $('<div class="alert alert-info" role="alert"></div>').append(
                    $("<strong>").text("Thank you! "),
                    document.createTextNode("Mail has been sent.")
                )
            );
        } catch (error) {
            console.error("OpenEduCat slide share email error:", error);
        }
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initEmbeddedViewer, { once: true });
} else {
    initEmbeddedViewer();
}
