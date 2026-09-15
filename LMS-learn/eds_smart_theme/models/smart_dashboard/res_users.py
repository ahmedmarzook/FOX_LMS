# -*- coding: utf-8 -*-
from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def action_get_smart_portal_nav(self):
        """Open My Profile via a dedicated action so refresh keeps the portal view."""
        if self.env.user.employee_id:
            action_xmlid = "eds_smart_theme.action_res_users_smart_portal_profile"
        else:
            action_xmlid = "eds_smart_theme.action_res_users_smart_portal_simple"
        action = self.env["ir.actions.act_window"]._for_xml_id(action_xmlid)
        action["res_id"] = self.env.user.id
        return action
