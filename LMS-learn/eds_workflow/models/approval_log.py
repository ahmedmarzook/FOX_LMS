"""
Created on Nov 2, 2017

@author: Zuhair Hammadi
"""

from odoo import models, fields, api


class ApprovalLog(models.Model):
    _name = "approval.log"
    _description = "Approval Workflow Log"
    _log_access = False
    _order = "id desc"

    model_id = fields.Many2one(
        "ir.model", string="Object", required=True, ondelete="cascade", index=True
    )
    record_id = fields.Integer(required=True, index=True)
    user_id = fields.Many2one("res.users", "User", required=True)

    state = fields.Char(required=True)

    name = fields.Char("New Status", compute="_calc_name")
    old_name = fields.Char(compute="_calc_old_name", string="Old Status")

    date = fields.Datetime("Date", required=True)

    description = fields.Text()

    old_state = fields.Char(compute="_calc_old_name")

    previous_log_id = fields.Many2one("approval.log", compute="_calc_old_name")

    @api.depends("state", "model_id")
    def _calc_name(self):
        for record in self:
            model = self.env.get(record.model_id.model)
            if model is None:
                record.name = False
                continue
            vals = dict(model._fields["state"]._description_selection(self.env))
            record.name = vals.get(record.state, record.state)

    @api.depends("name")
    def _calc_old_name(self):
        for record in self:
            last_log = self.search(
                [
                    ("model_id", "=", record.model_id.id),
                    ("record_id", "=", record.record_id),
                    ("id", "<", record.id),
                ],
                order="id desc",
                limit=1,
            )[:1]
            record.old_name = last_log.name
            record.old_state = last_log.state
            record.previous_log_id = last_log
