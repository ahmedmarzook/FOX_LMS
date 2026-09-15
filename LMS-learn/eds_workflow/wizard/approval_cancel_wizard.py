"""
Created on Sep 6, 2021

@author: Fatima Shubbar
"""

from odoo import models, fields, api
import json


class ApprovalCancelWizard(models.TransientModel):
    _name = "approval.cancel.wizard"
    _description = "Approval Cancel Wizard"

    @api.model
    def _get_state(self):
        model = self._context.get("active_model")
        if not model:
            return []

        selection = dict(
            self.env[model]._fields["state"]._description_selection(self.env)
        )
        record = self.env[model].browse(self._context.get("active_id"))
        workflow_states = json.loads(record.workflow_states)
        res = []
        for state in reversed(workflow_states):
            if state == record.state:
                break
            res.insert(0, (state, selection[state]))
        return res

    model = fields.Char(
        default=lambda self: self._context.get("active_model"), required=True
    )
    record_id = fields.Integer(
        default=lambda self: self._context.get("active_id"),
        required=True,
        string="Record ID",
    )
    record_ref = fields.Char("Record", compute="_calc_record_ref")

    state = fields.Selection(_get_state, string="Status")
    reason = fields.Text(required=True)

    @api.depends("model", "record_id")
    def _calc_record_ref(self):
        for wizard in self:
            record = self.env[wizard.model].browse(wizard.record_id).exists()
            wizard.record_ref = record and "%s,%d" % (record._name, record.id)

    def action_cancel(self):
        record = self.env[self.model].browse(self.record_id)
        if record.status_id.cancel_type == "auto_cancel":
            states = record._fields["state"].get_values(self.env)
            cancel_state = record._on_cancel()
            if cancel_state in states:
                record.write({"state": cancel_state})
            else:
                for state in ["canceled", "cancelled", "cancel"]:
                    if state in states:
                        if record.state != state:
                            record.with_context(reject_reason=self.reason).write(
                                {"state": state}
                            )
                        break
            record._remove_approval_activity(action="cancelled", reason=self.reason)

        elif record.status_id.cancel_type == "workflow":
            vals = {
                "model_id": self.env["ir.model"]
                .search([("model", "=", self.model)])
                .id,
                "model_name": self.model,
                "record_id": self.record_id,
                "reason": self.reason,
                "requester_id": self.env.user.id,
            }
            res = self.env["cancellation.record"].create(vals)
            res.action_approve()
            return {
                "view_type": "form",
                "view_mode": "form",
                "res_model": "cancellation.record",
                "type": "ir.actions.act_window",
                "target": "current",
                "res_id": res.id,
            }
