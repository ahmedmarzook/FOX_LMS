from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json


class ApprovalReturnWizard(models.TransientModel):
    _inherit = "approval.return.wizard"

    approval_state_id = fields.Many2one(
        comodel_name="approval.return.state",
        string="State",
        required=False,
    )
    approval_state_ids = fields.Many2many(comodel_name="approval.return.state")

    state = fields.Selection(required=False)

    def action_return(self):
        ctx = self.env.context.copy()
        fixed_return_state = ctx.get("fixed_return_state")
        state = fixed_return_state
        if not fixed_return_state:
            state = self.approval_state_id.state
            ctx.pop("default_state", False)
            ctx.pop("fixed_return_state", False)
        record = self.env[self.model].browse(self.record_id)

        # Edge case: No state selected - fallback to previous state in workflow
        if not state:
            workflow_states = json.loads(record.workflow_states or "[]")
            try:
                current_index = workflow_states.index(record.state)
                if current_index > 0:
                    # Return to the immediate previous state
                    state = workflow_states[current_index - 1]
                else:
                    # Already at first state, cannot return further
                    raise UserError(
                        _("Cannot return: already at the first workflow state.")
                    )
            except ValueError:
                raise UserError(
                    _("Cannot return: current state not found in workflow.")
                )

        # Add force_return context to bypass button_approve_enabled filter at last state
        ctx["force_return"] = True
        action = record.with_context(ctx)._action_return(state, self.reason)
        return action or {"type": "ir.actions.client", "tag": "soft_reload"}
