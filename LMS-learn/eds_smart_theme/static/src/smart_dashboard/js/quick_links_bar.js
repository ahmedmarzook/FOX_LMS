/** @odoo-module **/

import { Component, useRef } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { getUiDirection } from "./ui_direction";

export class QuickLinksBar extends Component {
    static template = "eds_smart_theme.QuickLinksBar";
    static props = {
        links: { type: Array, optional: true },
        title: { type: String, optional: true },
    };

    setup() {
        this.qlTrackRef = useRef("qlTrack");
        this.labelPrevious = _t("Previous");
        this.labelNext = _t("Next");
    }

    get displayLinks() {
        const raw = this.props.links;
        return Array.isArray(raw) ? raw : [];
    }

    linkTarget(href) {
        if (!href || href === "#") {
            return undefined;
        }
        const s = String(href).trim().toLowerCase();
        if (s.startsWith("http://") || s.startsWith("https://")) {
            return "_blank";
        }
        return undefined;
    }

    linkRel(href) {
        return this.linkTarget(href) === "_blank" ? "noopener noreferrer" : undefined;
    }

    qlScroll(delta) {
        const el = this.qlTrackRef.el;
        if (!el) {
            return;
        }
        const root = el.closest("[dir]") || document.documentElement;
        const isRtl = (root.getAttribute("dir") || getUiDirection()) === "rtl";
        el.scrollBy({ left: isRtl ? -delta : delta, behavior: "smooth" });
    }
}
