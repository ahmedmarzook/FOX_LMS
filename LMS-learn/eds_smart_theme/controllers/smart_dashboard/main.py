# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class EdsThemeSmartDashboardController(http.Controller):
    @http.route(
        "/eds_smart_theme/smart_dashboard/bootstrap",
        type="json",
        auth="user",
    )
    def smart_portal_bootstrap(self):
        return request.env["smart.portal.data"].get_bootstrap_payload()

    @http.route(
        "/eds_smart_theme/smart_dashboard/help_center_action",
        type="json",
        auth="user",
    )
    def help_center_action(self):
        return request.env["smart.portal.data"].get_help_center_action()

    @http.route(
        "/eds_smart_theme/smart_dashboard/employee_profile_action",
        type="json",
        auth="user",
    )
    def employee_profile_action(self):
        return request.env["smart.portal.data"].get_employee_profile_action()

    @http.route(
        "/eds_smart_theme/smart_dashboard/approve_activity",
        type="json",
        auth="user",
    )
    def approve_activity(self, activity_id):
        return request.env["smart.portal.data"].approve_pending_activity(activity_id)

    @http.route(
        "/eds_smart_theme/smart_dashboard/search",
        type="json",
        auth="user",
    )
    def smart_portal_search(self, search="", limit=50):
        return request.env["smart.portal.data"].search_portal_sections(
            search=search, limit=limit
        )
