"""
Created on Jul 14, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields, api
from odoo.tools.safe_eval import test_python_expr
from odoo.exceptions import ValidationError


class ApprovalSettings(models.Model):
    _name = "approval.settings"
    _inherit = ["cache.mixin"]
    _description = "Approval Workflow Model Settings"
    _rec_name = "model"
    _order = "model"

    model_id = fields.Many2one(
        "ir.model",
        string="Object",
        required=True,
        ondelete="cascade",
        domain=[("field_id.name", "=", "state"), ("transient", "=", False)],
    )

    model = fields.Char(related="model_id.model", store=True, readonly=True)
    model_name = fields.Char(related="model_id.name", readonly=True)

    state_ids = fields.One2many(
        "approval.settings.state", "settings_id", context={"active_test": False}
    )

    on_submit = fields.Text()
    on_approve = fields.Text()
    on_approval = fields.Text()
    on_reject = fields.Text()
    on_forward = fields.Text()
    on_return = fields.Text()
    on_transfer = fields.Text()

    approval_count = fields.Integer(compute="_calc_approval_count")

    show_action_approve_all = fields.Boolean(default=True)

    _sql_constraints = [
        ("model_uniq", "unique (model_id)", "The model should be unique !")
    ]

    @api.constrains(
        "on_submit",
        "on_approve",
        "on_approval",
        "on_reject",
        "on_forward",
        "on_return",
        "on_transfer",
    )
    def _check_code(self):
        for record in self:
            for name in (
                "on_submit",
                "on_approve",
                "on_approval",
                "on_reject",
                "on_forward",
                "on_return",
                "on_transfer",
            ):
                value = record[name]
                if value:
                    msg = test_python_expr(expr=value.strip(), mode="exec")
                    if msg:
                        raise ValidationError(msg)

    def _default_states(self):
        model = self.model_id.model
        sequence = 0
        res = []
        for state, name in self.env[model]._before_approval_states():
            sequence += 1
            res.append(
                {
                    "state": state,
                    "name": name,
                    "type": "before",
                    "sequence": sequence,
                    "settings_id": self.id,
                }
            )
        for state, name in self.env[model]._after_approval_states():
            sequence += 1
            res.append(
                {
                    "state": state,
                    "name": name,
                    "type": "after",
                    "sequence": sequence,
                    "reject_state": state == "rejected",
                    "settings_id": self.id,
                }
            )
        return res

    def reset_states(self):
        self.state_ids.unlink()

        lang_vals_list = {}
        for lang, __ in self.env["res.lang"].get_installed():
            lang_vals_list[lang] = self.with_context(lang=lang)._default_states()

        for lang, vals_list in lang_vals_list.items():
            for vals in vals_list:
                record = self.state_ids.filtered(
                    lambda state_id: state_id.state == vals["state"]
                )
                if not record:
                    record.with_context(lang=lang).create(vals)
                else:
                    record.with_context(lang=lang).name = vals["name"]

    @api.depends("model_id")
    def _calc_approval_count(self):
        for record in self:
            record.approval_count = self.env["approval.config"].search_count(
                [("model_id", "=", record.model_id.id)]
            )

    def action_view_approval(self):
        model_id = self.model_id.id
        return {
            "type": "ir.actions.act_window",
            "name": "Workflow",
            "res_model": "approval.config",
            "view_mode": ",form",
            "context": {"default_model_id": model_id},
            "domain": [("model_id", "=", model_id)],
        }

    @api.model
    def get(self, model):
        return self.search_cached([("model", "=", model)])

    @api.model
    def is_show_action_approve_all(self, model):
        return self.get(model).show_action_approve_all
