/** @odoo-module **/

import { formatDateTime } from "@web/core/l10n/dates";
import { formatFloat, formatInteger } from "@web/views/fields/formatters";

export const format = {
    float(value) {
        return formatFloat(Number(value || 0));
    },
    integer(value) {
        return formatInteger(Math.round(Number(value || 0)));
    },
    datetime(value) {
        try {
            return formatDateTime(value);
        } catch {
            return String(value || "");
        }
    },
};

const GlobalFunction = {
    number_shorthand_function(number, digits = 1) {
        let value = Number(number || 0);
        const negative = value < 0;
        value = Math.abs(value);
        const units = [
            [1e18, "E"],
            [1e15, "P"],
            [1e12, "T"],
            [1e9, "G"],
            [1e6, "M"],
            [1e3, "k"],
            [1, ""],
        ];
        const [factor, symbol] =
            units.find(([candidate]) => value >= candidate) || [1, ""];
        const formatted = (value / factor)
            .toFixed(digits)
            .replace(/\.0+$|(\.[0-9]*[1-9])0+$/, "$1");
        return `${negative ? "-" : ""}${formatted}${symbol}`;
    },

    currency_monetary_function(value, currency) {
        if (!currency) {
            return value;
        }
        if (typeof currency === "string") {
            return `${currency} ${value}`;
        }
        const symbol = currency.symbol || "";
        return currency.position === "after"
            ? `${value} ${symbol}`.trim()
            : `${symbol} ${value}`.trim();
    },

    convert_to_rgba_function(value) {
        const [rawColor = "#000000", rawOpacity = "1"] =
            String(value || "#000000,1").split(",");
        const color = rawColor.startsWith("#") ? rawColor.slice(1) : rawColor;
        const normalized =
            color.length === 3
                ? color.split("").map((part) => part + part).join("")
                : color.padEnd(6, "0").slice(0, 6);
        const channels = normalized
            .match(/.{2}/g)
            .map((part) => Number.parseInt(part, 16))
            .join(",");
        const opacity = Math.min(1, Math.max(0, Number(rawOpacity) || 0));
        return `rgba(${channels},${opacity})`;
    },
};

export default GlobalFunction;
