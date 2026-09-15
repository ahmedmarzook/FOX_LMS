/** @odoo-module **/
export function isHomeMenuAvailable(menuService) {
    return Boolean(menuService?.getApps?.().length);
}
