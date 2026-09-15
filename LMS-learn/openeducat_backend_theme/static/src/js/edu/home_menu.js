/** @odoo-module **/
export function filterApplications(apps, query) {
    const value = String(query || "").trim().toLowerCase();
    return value
        ? apps.filter((app) => app.name.toLowerCase().includes(value))
        : apps;
}
