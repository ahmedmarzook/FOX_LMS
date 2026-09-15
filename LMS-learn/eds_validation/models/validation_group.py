"""
Created on Jun 20, 2018

@author: Zuhair Hammadi
"""

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


class ValidationGroup(models.Model):
    _name = "validation.group"
    _description = "validation.group"
    _inherit = ["mail.thread"]

    _order = "sequence,id"

    name = fields.Char(required=True)

    sequence = fields.Integer(default=1)

    model_id = fields.Many2one(
        "ir.model", required=True, string="Object", ondelete="cascade"
    )

    model = fields.Char(related="model_id.model", readonly=True)

    active = fields.Boolean(default=True, tracking=True)

    valid_from = fields.Date(
        required=True, default=fields.Date.today, tracking=True
    )

    valid_to = fields.Date(tracking=True)

    validation_ids = fields.One2many("validation", "group_id", tracking=True)

    log_count = fields.Integer(compute="_calc_log_count")

    validation_count = fields.Integer(compute="_calc_validation_count")

    domain = fields.Text(default="[]", required=True)

    @api.depends("validation_ids")
    def _calc_validation_count(self):
        for record in self:
            record.validation_count = len(record.validation_ids)

    @api.depends("validation_ids.log_ids")
    def _calc_log_count(self):
        for record in self:
            record.log_count = self.env["validation.log"].search(
                [("validation_id", "in", record.validation_ids.ids)]
            )

    def action_log(self):
        action = self.env.ref("eds_validation.action_validation_log").read()[0]
        action["domain"] = [("validation_id.group_id", "=", self.id)]
        return action

    def action_items(self):
        action = self.env.ref("eds_validation.action_validation").read()[0]
        context = safe_eval(action.get("context") or "{}")
        context["default_group_id"] = self.id
        action["context"] = context
        action["domain"] = [("group_id", "=", self.id)]
        return action

    def copy_data(self, default=None):
        default = default or {}
        if "validation_ids" not in default:
            res = []
            for validation in self.validation_ids:
                res.append((0, 0, validation.copy_data()[0]))
            default["validation_ids"] = res
        return super(ValidationGroup, self).copy_data(default=default)

    @api.model_create_multi
    def create(self, vals_list):
        self.env["validation"].invalidate_model()
        return super(ValidationGroup, self).create(vals_list)

    def write(self, vals):
        self.env["validation"].invalidate_model()
        return super(ValidationGroup, self).write(vals)

    def unlink(self):
        self.env["validation"].invalidate_model()
        return super(ValidationGroup, self).unlink()
