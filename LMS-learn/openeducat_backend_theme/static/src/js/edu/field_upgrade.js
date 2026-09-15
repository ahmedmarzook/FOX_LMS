/** @odoo-module **/
export function normalizeThemeFieldValue(value, fallback = "") {
    return value === undefined || value === null ? fallback : value;
}
