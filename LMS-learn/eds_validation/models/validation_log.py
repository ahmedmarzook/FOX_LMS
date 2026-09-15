"""
Created on Jun 5, 2018

@author: Zuhair Hammadi
"""

from odoo import models, fields, api


class Validation(models.Model):
    _name = "validation.log"
    _description = "validation.log"
    _log_access = False

    user_id = fields.Many2one("res.users", required=True, string="User")

    date = fields.Datetime(required=True)

    res_id = fields.Integer(required=True, string="Record ID")
    validation_id = fields.Many2one("validation", required=True, ondelete="cascade")

    model_id = fields.Many2one(
        "ir.model", related="validation_id.model_id", readonly=True
    )
    model = fields.Char(related="validation_id.model_id.model", readonly=True)

    reference = fields.Char(string="Reference", compute="_compute_reference")

    reference_title = fields.Char(string="Record", compute="_compute_reference_title")

    name = fields.Char(compute="_calc_name")

    message = fields.Text()

    on_create = fields.Boolean("On Creation")
    on_write = fields.Boolean("On Update")
    be_write = fields.Boolean("Before Update")
    on_unlink = fields.Boolean("On Deletion")

    @api.depends("model", "res_id")
    def _compute_reference(self):
        for record in self:
            if (
                record.model
                and record.res_id
                and self.env[record.model].browse(record.res_id).exists()
            ):
                record.reference = "%s,%s" % (record.model, record.res_id)

    @api.depends("model", "res_id")
    def _compute_reference_title(self):
        for record in self:
            if record.model and record.res_id:
                record.reference_title = (
                    self.env[record.model].browse(record.res_id).exists().display_name
                )

    @api.depends("validation_id", "date")
    def _calc_name(self):
        for record in self:
            record.name = "%s %s" % (
                record.validation_id.name,
                self.env["ir.qweb.field.datetime"].value_to_html(record.date, {}),
            )
