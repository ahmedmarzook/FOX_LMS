"""
Created on Jan 08, 2024

@author: Elyas
"""

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class ShowAsService(models.TransientModel):
    _name = "show.as.service.wizard"
    _description = "Show As Service Wizard"

    model_id = fields.Many2one("ir.model", required=True, string="Object")
    category_id = fields.Many2one("approval.model.category", required=True)

    def create_approval_model(self):
        if self.env["approval.model"].search([("model_id", "=", self.model_id.id)]):
            raise ValidationError(_("The object is already exist."))

        self.env["approval.model"].create(
            {"model_id": self.model_id.id, "category_id": self.category_id.id}
        )
