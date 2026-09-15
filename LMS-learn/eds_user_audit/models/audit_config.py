"""
Created on Aug 27, 2018

@author: Admin
"""

from odoo import models, fields, api, tools
from odoo.osv import expression
from .. import READ, CREATE, WRITE, UNLINK


class AuditConfig(models.Model):
    _name = "audit.config"
    _description = "audit.config"

    name = fields.Char(required=True)
    user_ids = fields.Many2many("res.users")

    all_user = fields.Boolean("All Users")

    model_ids = fields.Many2many(
        "ir.model",
        string="Object",
        domain=[("transient", "=", False), ("model", "not like", "audit.%")],
    )

    field_ids = fields.Many2many(
        "ir.model.fields",
        string="Fields",
        domain="[('model_id','=', model_ids), ('store', '=', True), ('name', 'not in', ['id', 'create_date', 'create_uid', 'write_date', 'write_uid'])]",
    )

    on_read = fields.Boolean("Read")
    on_write = fields.Boolean("Write")
    on_create = fields.Boolean("Create")
    on_unlink = fields.Boolean("Delete")

    active = fields.Boolean(default=True)

    full_log = fields.Boolean("Full Log")

    @api.model
    @tools.ormcache("self.env.uid", "model", "operation")
    def _get_audit_config(self, model, operation):
        if not self.env.registry.ready:
            return
        operation = {
            READ: "on_read",
            CREATE: "on_create",
            WRITE: "on_write",
            UNLINK: "on_unlink",
        }[operation]
        model_id = self.env["ir.model"]._get_id(model)
        return (
            self.sudo()
            .search(
                [
                    ("model_ids", "=", model_id),
                    ("active", "=", True),
                    (operation, "=", True),
                    "|",
                    ("all_user", "=", True),
                    ("user_ids", "=", self.env.uid),
                ]
            )
            ._ids
            or None
        )

    @api.model
    def _get_audit_domain(self):
        IrRule = self.env["ir.rule"]
        domains = []
        for model_id in self.sudo().search([("active", "=", True)]).mapped("model_ids"):
            if model_id.model not in self.env:
                continue
            if not self.env[model_id.model].check_access_rights("read", False):
                domains.append([("model_id", "!=", model_id.id)])
                continue
            model_domain = IrRule._compute_domain(model_id.model)
            if model_domain:
                ids = self.env[model_id.model].sudo().search(model_domain)._ids or [0]
                domains.append(
                    [
                        "|",
                        "|",
                        ("model_id", "!=", model_id.id),
                        ("record_id", "in", ids),
                        ("type", "=", 4),
                    ]
                )
        if not domains:
            return []
        return expression.AND(domains)
