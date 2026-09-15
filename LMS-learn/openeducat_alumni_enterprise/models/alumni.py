# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import _, fields, models
from odoo.exceptions import UserError


class OpAlumni(models.Model):
    _inherit = "op.student"

    alumni_boolean = fields.Boolean(string="Alumni Student")
    passing_year_id = fields.Many2one("op.batch", string="Passing Year")
    current_position = fields.Char(string="Current Position")
    current_job = fields.Char(string="Current Job")
    alumni_id = fields.Many2one("op.alumni.group", string="Group")
    invoice_id = fields.Many2one("account.move", string="Invoice", copy=False, readonly=True)
    number = fields.Char(related="invoice_id.name", string="Invoice Number", readonly=True)
    join_date = fields.Date(related="invoice_id.invoice_date", string="Join Date", readonly=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("invoice", "Invoice Created"),
        ("cancel", "Cancelled"),
    ], string="Status", default="draft", copy=False)

    def get_invoice(self):
        for student in self:
            if student.invoice_id:
                raise UserError(_("An invoice has already been created for this alumnus."))
            group = student.alumni_id
            if not group or not group.fees_id:
                raise UserError(_("Configure an alumni group and fee product first."))
            if group.alumni_fees_amount <= 0:
                raise UserError(_("The alumni fee amount must be positive."))
            if not student.partner_id:
                raise UserError(_("The student must have a related contact before creating an invoice."))

            product = group.fees_id
            account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
            if not account:
                raise UserError(_("No income account is configured for product %s.") % product.display_name)

            invoice = self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": student.partner_id.id,
                "invoice_date": fields.Date.context_today(student),
                "invoice_line_ids": [(0, 0, {
                    "name": group.name or product.display_name,
                    "account_id": account.id,
                    "price_unit": group.alumni_fees_amount,
                    "quantity": 1.0,
                    "product_id": product.id,
                    "product_uom_id": product.uom_id.id,
                })],
            })
            student.write({"state": "invoice", "invoice_id": invoice.id})
        return True

    def action_get_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("Invoice"),
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": self.invoice_id.id,
            "target": "current",
        }
