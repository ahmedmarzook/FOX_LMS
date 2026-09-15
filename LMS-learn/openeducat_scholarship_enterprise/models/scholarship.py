# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class OpScholarship(models.Model):
    _name = "op.scholarship"
    _description = "Scholarship"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "student_id"
    _order = "id desc"

    name = fields.Char(
        string="Name",
        required=True,
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
        tracking=True,
        index=True,
    )
    sponsor_id = fields.Many2one(
        "res.partner",
        string="Sponsor",
        tracking=True,
        ondelete="restrict",
    )
    student_id = fields.Many2one(
        "op.student",
        string="Student",
        required=True,
        tracking=True,
        ondelete="cascade",
    )
    type_id = fields.Many2one(
        "op.scholarship.type",
        string="Type",
        required=True,
        tracking=True,
        ondelete="restrict",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
        ondelete="cascade",
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        tracking=True,
    )
    course_id = fields.Many2one(
        "op.course",
        string="Course",
        tracking=True,
        ondelete="restrict",
    )
    batch_id = fields.Many2one(
        "op.batch",
        string="Batch",
        tracking=True,
        ondelete="restrict",
    )
    active = fields.Boolean(default=True)
    scholarship_stages_id = fields.Many2one(
        "scholarship.stages",
        string="Scholarship Stage",
        ondelete="restrict",
        tracking=True,
        group_expand="_read_group_scholarship_stages_id",
        default=lambda self: self.env.ref(
            "openeducat_scholarship_enterprise.op_scholarship_stages_1",
            raise_if_not_found=False,
        ),
    )
    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
        readonly=True,
        copy=False,
        ondelete="set null",
    )

    @api.model
    def _read_group_scholarship_stages_id(self, stages, domain):
        return self.env["scholarship.stages"].search([], order="sequence, id")

    @api.onchange("course_id")
    def _onchange_course_id(self):
        if not self.course_id:
            self.batch_id = False
            return {"domain": {"batch_id": []}}
        if self.batch_id and self.batch_id.course_id != self.course_id:
            self.batch_id = False
        return {
            "domain": {
                "batch_id": [("course_id", "=", self.course_id.id)],
            },
        }

    @api.onchange("type_id")
    def _onchange_type_id(self):
        if self.type_id:
            self.amount = self.type_id.amount

    @api.constrains("amount")
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_("Scholarship amount must be greater than zero."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("op.scholarship")
                    or _("New")
                )
        return super().create(vals_list)

    def make_invoices(self):
        self.ensure_one()

        if self.invoice_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "account.move",
                "view_mode": "form",
                "res_id": self.invoice_id.id,
                "target": "current",
            }

        if not self.sponsor_id:
            raise UserError(_("Select a sponsor before creating an invoice."))
        if not self.sponsor_id.property_account_receivable_id:
            raise UserError(_("The sponsor does not have a receivable account."))

        income_account = self.env["account.account"].search(
            [
                ("company_ids", "in", self.company_id.id),
                ("account_type", "=", "income"),
                ("deprecated", "=", False),
            ],
            limit=1,
        )
        if not income_account:
            raise UserError(
                _("Configure at least one income account for the scholarship company.")
            )

        description_parts = [
            _("Scholarship"),
            self.student_id.name or "",
            self.course_id.name if self.course_id else "",
            self.batch_id.name if self.batch_id else "",
        ]
        description = " - ".join(part for part in description_parts if part)

        invoice = self.env["account.move"].with_company(self.company_id).create({
            "partner_id": self.sponsor_id.id,
            "move_type": "out_invoice",
            "invoice_date": fields.Date.context_today(self),
            "company_id": self.company_id.id,
            "invoice_origin": self.name,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": description,
                        "account_id": income_account.id,
                        "price_unit": self.amount,
                        "quantity": 1.0,
                    },
                ),
            ],
        })
        self.invoice_id = invoice

        return {
            "type": "ir.actions.act_window",
            "name": _("Scholarship Invoice"),
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": invoice.id,
            "target": "current",
        }
