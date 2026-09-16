/** @odoo-module **/

import { cookie } from "@web/core/browser/cookie";

const FULLSCREEN_COOKIE = "lms_full";
const COOKIE_DURATION = 60 * 60 * 24 * 365;

function setFullscreenState(isFullscreen) {
    const materialView = $("#material_view");

    if (!materialView.length) {
        return;
    }

    materialView
        .toggleClass("fullscreen", isFullscreen)
        .toggleClass("main-screen", !isFullscreen);

    const isCoursePage =
        window.location.pathname.startsWith(
            "/course"
        );

    if (isCoursePage) {
        $("#wrapwrap").toggleClass(
            "active",
            isFullscreen
        );

        $(".lms_course_sidebar").toggleClass(
            "active",
            isFullscreen
        );
    }

    if (isFullscreen) {
        $(".lms_sidebar_enable")
            .css("padding-left", "0px")
            .addClass("lms_sidebar_disable")
            .removeClass("lms_sidebar_enable");
    } else {
        $(".lms_sidebar_disable")
            .css("padding-left", "350px")
            .addClass("lms_sidebar_enable")
            .removeClass("lms_sidebar_disable");
    }
}

function saveFullscreenState(isFullscreen) {
    cookie.set(
        FULLSCREEN_COOKIE,
        isFullscreen ? "full" : "sidebar",
        COOKIE_DURATION
    );
}

function createPreviewDialog() {
    const thumbnailLink = $(
        ".course-thumbnail > a"
    ).first();

    if (!thumbnailLink.length) {
        return;
    }

    const previewContent =
        thumbnailLink.clone();

    previewContent
        .find("video")
        .attr("controls", "controls");

    previewContent
        .find("iframe")
        .removeClass("d-none")
        .css({
            height: "100%",
            width: "100%",
            border: "0",
        });

    previewContent
        .find("img")
        .addClass("d-none");

    const dialog =
        document.createElement("dialog");

    dialog.className =
        "o_lms_content_preview";

    Object.assign(dialog.style, {
        width: "90vw",
        maxWidth: "1200px",
        height: "90vh",
        padding: "0",
        border: "0",
        borderRadius: "8px",
        overflow: "hidden",
    });

    const header =
        document.createElement("div");

    Object.assign(header.style, {
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "12px 16px",
        borderBottom: "1px solid #dee2e6",
        backgroundColor: "#ffffff",
    });

    const title =
        document.createElement("h4");

    title.className = "m-0";
    title.textContent =
        $(
            ".course-detail-h2.course_name"
        ).text();

    const closeButton =
        document.createElement("button");

    closeButton.type = "button";
    closeButton.className = "btn-close";
    closeButton.setAttribute(
        "aria-label",
        "Close"
    );

    closeButton.addEventListener(
        "click",
        function () {
            dialog.close();
        }
    );

    header.append(title, closeButton);

    const body =
        document.createElement("div");

    Object.assign(body.style, {
        width: "100%",
        height: "calc(90vh - 60px)",
        overflow: "auto",
        backgroundColor: "#ffffff",
    });

    const clonedElements =
        previewContent.contents().toArray();

    body.append(...clonedElements);

    dialog.append(header, body);
    document.body.appendChild(dialog);

    dialog.addEventListener(
        "click",
        function (event) {
            if (event.target === dialog) {
                dialog.close();
            }
        }
    );

    dialog.addEventListener(
        "close",
        function () {
            dialog.remove();
        },
        {
            once: true,
        }
    );

    dialog.showModal();
}

$(function () {
    $(document)
        .off(
            "click.openeducatFullscreen",
            ".fullscreenwidget"
        )
        .on(
            "click.openeducatFullscreen",
            ".fullscreenwidget",
            function (event) {
                event.preventDefault();

                const materialView =
                    $("#material_view");

                if (!materialView.length) {
                    return;
                }

                const isFullscreen =
                    !materialView.hasClass(
                        "fullscreen"
                    );

                setFullscreenState(isFullscreen);
                saveFullscreenState(isFullscreen);
            }
        );

    if (
        $("#material_view").length &&
        window.location.pathname.startsWith(
            "/course"
        ) &&
        cookie.get(FULLSCREEN_COOKIE) ===
            "full"
    ) {
        setFullscreenState(true);
    }

    $(document)
        .off(
            "click.openeducatPreview",
            ".course-thumbnail.detail-page"
        )
        .on(
            "click.openeducatPreview",
            ".course-thumbnail.detail-page",
            function (event) {
                const hasDirectImage = $(
                    ".course-thumbnail.detail-page > a"
                )
                    .children()
                    .is("img");

                if (hasDirectImage) {
                    return;
                }

                event.preventDefault();
                createPreviewDialog();
            }
        );
});