# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import http
from odoo.http import request


class OnboardingController(http.Controller):

    @http.route(
        "/openeducat_parent_enterprise/openeducat_parent_onboarding_panel",
        auth="user",
        type="jsonrpc",
    )
    def openeducat_parent_onboarding_panel(self):
        company = request.env.user.company_id
        if (
            not request.env.user._is_admin()
            or company.openeducat_parent_onboard_panel == "closed"
        ):
            return {}

        html = request.env["ir.qweb"]._render(
            "openeducat_parent_enterprise.openeducat_parent_onboarding_panel",
            {
                "company": company,
                "state": company.update_parent_onboarding_state(),
            },
        )
        return {"html": str(html)}
