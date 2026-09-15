from odoo import models, fields, api
import json


class ApprovalTransferWizard(models.TransientModel):
    _inherit = "approval.transfer.wizard"

    approval_state_id = fields.Many2one(
        comodel_name="approval.transfer.state",
        string="State",
        required=False,
    )
    approval_state_ids = fields.Many2many(comodel_name="approval.transfer.state")

    state = fields.Selection(required=False)

    def action_transfer(self):
        ctx = self.env.context.copy()
        ctx.pop("default_state", False)
        ctx.pop("fixed_transfer_state", False)
        record = self.env[self.model].browse(self.record_id)
        action = record.with_context(ctx)._action_transfer(
            self.approval_state_id.state, self.reason
        )
        return action or {"type": "ir.actions.client", "tag": "soft_reload"}
