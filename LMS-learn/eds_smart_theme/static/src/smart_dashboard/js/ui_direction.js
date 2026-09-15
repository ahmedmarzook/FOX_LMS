/** @odoo-module **/

import { localization } from "@web/core/l10n/localization";
import { session } from "@web/session";

export const SMART_UI_DIRECTION_EVENT = "smart-ui-direction";

const RTL_LANG_RE = /^(ar|he|fa|ur)(@|_|$)/i;

/** Odoo sets body.o_rtl + localization.direction; html[dir] is often unset. */
export function getUiDirection() {
    const dir = localization.direction;
    if (dir === "rtl" || dir === "ltr") {
        return dir;
    }
    const lang = session.user_context?.lang || "";
    if (lang) {
        return RTL_LANG_RE.test(lang) ? "rtl" : "ltr";
    }
    return document.body.classList.contains("o_rtl") ? "rtl" : "ltr";
}

/** Opposite of page direction so flex order matches the designed toolbar layout. */
function invertDirection(dir) {
    return dir === "rtl" ? "ltr" : "rtl";
}

/**
 * `dir` for the patched backend navbar (`t-att-dir` on `.o_main_navbar`).
 * Inverted vs page direction so tools/brand land on the correct visual sides.
 */
export function getNavBarDirection() {
    return invertDirection(getUiDirection());
}

/**
 * Navbar `dir` while Smart Portal is the active action (page passes its own `dir`).
 */
export function getNavDirectionForPortal(pageDir) {
    const base =
        pageDir === "rtl" || pageDir === "ltr"
            ? pageDir
            : getUiDirection();
    return invertDirection(base);
}

/** Tell the patched navbar to refresh portal nav direction (pass dashboard `dir`). */
export function notifyUiDirection(pageDir) {
    const dir = pageDir === "rtl" || pageDir === "ltr" ? pageDir : getUiDirection();
    document.dispatchEvent(
        new CustomEvent(SMART_UI_DIRECTION_EVENT, { bubbles: true, detail: { dir } })
    );
}

export function getUiLocale() {
    const code = localization.code;
    if (code) {
        return code === "sr@latin" ? "sr-Latn-RS" : code.replace(/_/g, "-");
    }
    return document.documentElement.lang || "en-US";
}

/** True when the signed-in user language is Arabic (or another RTL locale we treat as Arabic UI). */
export function isUiArabic() {
    const lang = session.user_context?.lang || localization.code || "";
    return RTL_LANG_RE.test(lang);
}
