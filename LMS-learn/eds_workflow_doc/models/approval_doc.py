"""
Created on Mar 27, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields, api, _
from collections import OrderedDict
from odoo.exceptions import UserError
import datetime


class ApprovalDocument(models.AbstractModel):
    _name = "approval.doc"
    _description = _name
    _inherit = ["approval.record", "mail.thread", "mail.activity.mixin"]

    name = fields.Char("Number", required=True, readonly=True, default=_("New"))
    state = fields.Selection(index=True)
    requester_id = fields.Many2one(
        "hr.employee", default=lambda self: self.env.user.employee_ids.id, readonly=True
    )
    requester_department_id = fields.Many2one(
        "hr.department",
        default=lambda self: self.env.user.employee_ids.department_id.id,
        readonly=True,
    )
    initail_submit_date = fields.Datetime(readonly=True)
    submit_date = fields.Datetime(readonly=True)
    approve_date = fields.Datetime(readonly=True)

    @api.model
    def _create_config_menu(self):
        return

    @api.model
    def _config_menu_resequence(self):
        return

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code(self._name)
        return super(ApprovalDocument, self).create(vals_list)

    def get_excel(self, ref):
        excel = self.env.ref(ref)
        rows = []
        for record in self:
            row = OrderedDict()
            for field in excel.field_ids:
                value = record[field.field_id.name]
                if isinstance(value, models.BaseModel):
                    value = ", ".join(value.mapped("display_name"))
                elif isinstance(value, datetime.datetime):
                    value = self.env["ir.qweb.field.datetime"].value_to_html(value, {})
                elif isinstance(value, datetime.date):
                    value = self.env["ir.qweb.field.date"].value_to_html(value, {})

                row[field.field_id.field_description] = value
            rows.append(row)
        return self.env["eds_excel_export"].export(rows, filename=excel.name)

    def unlink(self):
        if any(self.filtered(lambda record: record.state != "draft")):
            raise UserError(_("You can delete draft status only"))
        return super(ApprovalDocument, self).unlink()

    def _on_submit(self):
        if not self.initail_submit_date:
            self.initail_submit_date = fields.Datetime.now()
        self.submit_date = fields.Datetime.now()

    def _on_approve(self):
        super(ApprovalDocument, self)._on_approve()
        self.approve_date = fields.Datetime.now()
