"""
Created on Dec 21, 2016

@author: zuhair
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DelegationLine(models.Model):
    _name = "delegation.line"
    _description = "Delegation Line"
    _order = "id"

    delegation_id = fields.Many2one(
        "delegation", string="Delegation Number", required=True, ondelete="cascade"
    )
    group_id = fields.Many2one("res.groups", string="Role", required=False)
    group_id_display = fields.Many2one(related="group_id", readonly=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Delegated Employee", required=False
    )
    user_id = fields.Many2one(
        "res.users",
        string="Delegated User",
        related="employee_id.user_id",
        store=True,
        index=True,
        readonly=True,
    )

    # related from delegation_id
    one_employee = fields.Boolean(
        "All role to one employee", related="delegation_id.one_employee", readonly=True
    )
    delegator_id = fields.Many2one(
        "hr.employee",
        string="Delegator",
        related="delegation_id.employee_id",
        readonly=True,
    )
    delegator_user_id = fields.Many2one(
        "res.users",
        string="Delegator User",
        related="delegation_id.user_id",
        store=True,
        index=True,
        readonly=True,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("revoked", "Revoked")],
        related="delegation_id.state",
        string="Status",
        copy=False,
        store=True,
        readonly=True,
    )

    date_from = fields.Date(
        "From Date", related="delegation_id.date_from", store=True, readonly=True
    )
    date_to = fields.Date(
        "To Date", related="delegation_id.date_to", store=True, readonly=True
    )

    active = fields.Boolean(default=True)

    # _sql_constraints = [
    #     ("group_uk", "unique(delegation_id, group_id)", "Role should be unique"),
    # ]

    @api.model
    def get(self, domain):
        "get active delegation"
        today = fields.Date.today()
        domain = [
            ("active", "=", True),
            ("state", "=", "confirmed"),
            ("date_from", "<=", today),
            ("date_to", ">=", today),
        ] + domain
        return self.search_fetch(domain, ["user_id", "delegator_user_id", "group_id"])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("delegation_id"):
                delegation = self.env["delegation"].browse(vals["delegation_id"])
                if delegation.one_employee:
                    vals["employee_id"] = delegation.delegateTo_employee_id.id
        return super(DelegationLine, self).create(vals_list)

    @api.constrains("employee_id", "delegator_id")
    def _user_check(self):
        for record in self:
            if record.employee_id == record.delegator_id:
                raise ValidationError(
                    _("The delegator should not been able to delegate himself")
                )
