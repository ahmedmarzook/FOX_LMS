from odoo import models, fields, api

class ApprovalEscalation(models.Model):
    _name = "approval.escalation"
    _description = "Approval Workflow Escalation"
    _order = "sequence,id"
    _inherits = {"base.automation": "automation_id"}  # delegation to base.automation

    # link to the parent model (must be required=True and ondelete='cascade')
    automation_id = fields.Many2one(
        "base.automation",
        string="Automated Action",
        required=True,
        ondelete="cascade",
    )

    config_id = fields.Many2one(
        "approval.config",
        string="Approval Config",
        required=False,
    )
    active = fields.Boolean(
        related="automation_id.active",
        store=True,
        readonly=False,
    )
    sequence = fields.Integer()

    @api.model
    def create(self, vals):
        # Ensure automation_id is always provided/created
        if "automation_id" not in vals:
            automation = self.env["base.automation"].create({})
            vals["automation_id"] = automation.id
        return super().create(vals)

    def unlink(self):
        # Let Odoo handle unlink of automation_id via _inherits
        return super().unlink()