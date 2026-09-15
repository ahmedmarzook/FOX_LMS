/** @odoo-module **/
import { browser } from "@web/core/browser/browser";

export function isCompactViewport() {
    return browser.innerWidth < 768;
}
