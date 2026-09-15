"""
Created on Aug 28, 2018

@author: Zuhair Hammadi
"""

from odoo import models, fields, api
from .. import WRITE


class AuditLog(models.Model):
    _name = "audit.log.detail"
    _description = "audit.log.detail"
    _log_access = False

    log_id = fields.Many2one("audit.log", required=True, ondelete="cascade")

    field_id = fields.Many2one(
        "ir.model.fields", string="Field", required=True, ondelete="cascade"
    )

    old_value = fields.Char("Old Value")
    new_value = fields.Char("New Value")

    user_id = fields.Many2one("res.users", related="log_id.user_id", readonly=True)
    date = fields.Datetime(related="log_id.date", readonly=True)

    reference = fields.Char(
        string="Reference", compute="_compute_reference", search="_search_reference"
    )

    field_name = fields.Char(
        related="field_id.field_description", string="Field Label", readonly=True
    )

    old_value_display = fields.Char("Old Value", compute="_calc_display_value")
    new_value_display = fields.Char("New Value", compute="_calc_display_value")

    @api.depends("log_id")
    def _compute_reference(self):
        for record in self:
            record.reference = record.log_id.reference

    def _search_reference(self, operator, value):
        assert operator == "="
        model, record_id = value.split(",")
        log_ids = (
            self.env["audit.log"]
            .search(
                [
                    ("model_id.model", "=", model),
                    ("record_id", "=", record_id),
                    ("type", "=", WRITE),
                ]
            )
            .ids
        )
        return [("log_id", "in", log_ids)]

    @api.depends("old_value", "new_value")
    def _calc_display_value(self):
        for record in self:
            if record.field_id.ttype == "boolean":
                format_value = lambda value: value or "False"
            elif record.field_id.ttype == "date":
                format_value = lambda value: self.env[
                    "ir.qweb.field.date"
                ].value_to_html(value, {})
            elif record.field_id.ttype == "datetime":
                format_value = lambda value: self.env[
                    "ir.qweb.field.datetime"
                ].value_to_html(value, {})
            elif record.field_id.ttype == "selection":
                field = self.env[record.log_id.model_id.model]._fields[
                    record.field_id.name
                ]
                values = dict(field._description_selection(self.env))
                format_value = lambda value: values.get(value, value)
            else:
                format_value = lambda value: value
            record.old_value_display = format_value(record.old_value)
            record.new_value_display = format_value(record.new_value)
