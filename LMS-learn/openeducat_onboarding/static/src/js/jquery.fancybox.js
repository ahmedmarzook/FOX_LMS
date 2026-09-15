/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * Odoo 19 compatible lightweight replacement for the old jQuery fancybox file.
 * The old library depends on global jQuery plugins and can break OWL asset loading.
 * This service keeps onboarding video/document links usable without loading legacy jQuery.
 */
export const openEducatFancyboxService = {
    start() {
        document.addEventListener("click", (ev) => {
            const link = ev.target.closest("a[data-fancybox]");
            if (!link) {
                return;
            }

            const href = link.getAttribute("href");
            if (!href) {
                return;
            }

            ev.preventDefault();
            ev.stopPropagation();
            window.open(href, "_blank", "noopener,noreferrer");
        });
    },
};

registry.category("services").add("openeducat_onboarding_fancybox", openEducatFancyboxService);
