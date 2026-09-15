/** @odoo-module **/

export function expandDashboardDomain(domain, context = {}) {
    return String(domain || "[]")
        .replaceAll('"%UID"', String(context.uid || 0))
        .replaceAll('"%MYCOMPANY"', String(context.companyId || 0));
}
