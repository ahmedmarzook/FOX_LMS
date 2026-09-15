/** @odoo-module **/
import { browser } from "@web/core/browser/browser";

export function getResponsiveMode() {
    if (browser.innerWidth < 768) {
        return "mobile";
    }
    if (browser.innerWidth < 1200) {
        return "tablet";
    }
    return "desktop";
}
