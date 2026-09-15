from odoo import models, fields, api


class ApprovalForwardWizard(models.TransientModel):
    _inherit = "approval.forward.wizard"
    reason = fields.Text(required=False)
