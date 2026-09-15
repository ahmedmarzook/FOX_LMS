"""
Created on Jan 11, 2017

@author: Zuhair Hammadi
"""

from odoo import models, fields
import logging
import re

pattern = re.compile(r";|,")

_logger = logging.getLogger(__name__)


class EmailTemplate(models.Model):
    _inherit = "mail.template"

    delegation_group_ids = fields.Many2many(
        "res.groups",
        "res_groups_delegation_templates",
        "template_id",
        "group_id",
        "Delegation Groups",
        domain=[("allow_delegation", "=", True)],
    )

    def generate_email(self, res_ids, fields=None):
        res = super(EmailTemplate, self).generate_email(res_ids, fields=fields)
        if isinstance(res_ids, int):
            res["template_id"] = self.id
        else:
            for vals in res.values():
                vals["template_id"] = self.id
        return res

    def add_delegation_email(self, res):

        def filter_email(email_list):
            email_list = map(lambda s: s.strip(), email_list)
            email_list = filter(None, email_list)
            return list(set(email_list))

        if self.delegation_group_ids:
            today = fields.Date.today()
            email_to = pattern.split(res.get("email_to", "")) + pattern.split(
                res.get("email_cc", "")
            )
            email_to = filter_email(email_to)
            employees = (
                self.env["hr.employee"].sudo().search([("work_email", "in", email_to)])
            )
            if res.get("recipient_ids"):
                partner_ids = [
                    r[1] for r in res["recipient_ids"] if len(r) == 2 and r[0] == 4
                ]
                employees |= (
                    self.env["res.users"]
                    .sudo()
                    .search([("partner_id", "in", partner_ids)])
                    .mapped("employee_ids")
                )
            if not employees:
                return
            delegations = (
                self.env["delegation"]
                .sudo()
                .search(
                    [
                        ("employee_id", "in", employees._ids),
                        ("state", "=", "confirmed"),
                        ("date_from", "<=", today),
                        ("date_to", ">=", today),
                    ]
                )
            )
            if not delegations:
                return
            delegations_lines = (
                self.env["delegation.line"]
                .sudo()
                .search(
                    [
                        ("delegation_id", "in", delegations._ids),
                        ("group_id", "in", self.delegation_group_ids._ids),
                        ("employee_id", "!=", False),
                    ]
                )
            )
            email_cc = pattern.split(res.get("email_cc", "")) + list(
                delegations_lines.mapped("employee_id.work_email")
            )
            email_cc = filter_email(email_cc)
            res["email_cc"] = "; ".join(email_cc)
