"""
Created on Aug 26, 2018

@author: Admin
"""

from odoo import models, fields, api
from _collections import defaultdict
from odoo.osv import expression
from .. import READ, CREATE, WRITE, UNLINK


class AuditLog(models.Model):
    _name = "audit.log"
    _description = "audit.log"
    _log_access = False

    name = fields.Char()
    record_id = fields.Integer(required=True, string="Record ID", group_operator="")
    model_id = fields.Many2one(
        "ir.model", string="Object", required=True, ondelete="cascade"
    )

    user_id = fields.Many2one(
        "res.users", required=True, string="User", ondelete="cascade"
    )
    date = fields.Datetime(required=True)

    type = fields.Selection(
        [(READ, "Read"), (CREATE, "Create"), (WRITE, "Write"), (UNLINK, "Delete")],
        required=True,
    )

    reference = fields.Char(
        string="Reference", compute="_compute_reference", readonly=True, store=False
    )

    detail_ids = fields.One2many("audit.log.detail", "log_id")

    action_id = fields.Many2one(
        "ir.actions.act_window", string="Action", ondelete="set null"
    )

    menu_ids = fields.Many2many("ir.ui.menu", string="Menu", compute="_calc_menu_ids")

    @api.depends("record_id")
    def _compute_reference(self):
        for log in self:
            if log.model_id.model not in self.env:
                log.reference = False
                continue
            record = self.env[log.model_id.model].browse(log.record_id)
            if record.exists():
                log.reference = "%s,%s" % (record._name, record.id)
            else:
                log.reference = False

    @api.depends("user_id")
    def _calc_menu_ids(self):
        for record in self:
            record.menu_ids = (
                self.env["ir.ui.menu"]
                .with_user(record.user_id.id)
                .search(
                    [
                        (
                            "action",
                            "=",
                            "ir.actions.act_window,%s" % record.action_id.id or 0,
                        )
                    ]
                )
            )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, *, active_test=True, bypass_access=False):
        if not self.env.su and not self.env.user.has_group(
            "eds_user_audit.group_audit_admin"
        ):
            audit_domain = self.env["audit.config"]._get_audit_domain()
            if audit_domain:
                if domain:
                    domain = expression.AND([domain, audit_domain])
                else:
                    domain = audit_domain
        return super(AuditLog, self)._search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
            active_test=active_test,
            bypass_access=bypass_access,
        )
