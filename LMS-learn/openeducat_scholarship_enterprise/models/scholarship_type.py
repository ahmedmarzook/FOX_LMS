# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpScholarshipType(models.Model):
    _name = "op.scholarship.type"
    _description = "Scholarship Type"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        ondelete="cascade",
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
    )
    active = fields.Boolean(default=True)

    @api.constrains("amount")
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_("Enter a valid amount greater than zero."))

    _sql_constraints = [
        (
            "scholarship_type_name_company_unique",
            "unique(name, company_id)",
            "The scholarship type must be unique per company.",
        ),
    ]
