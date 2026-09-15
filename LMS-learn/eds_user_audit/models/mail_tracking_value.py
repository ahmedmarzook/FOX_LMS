"""
Created on Sep 3, 2018

@author: Zuhair Hammadi
"""

from odoo import models, fields, api


class MailTracking(models.Model):
    _inherit = "mail.tracking.value"

    old_value = fields.Char("Old Value", compute="_calc_value")
    new_value = fields.Char("New Value", compute="_calc_value")

    reference = fields.Char(
        string="Reference", compute="_compute_reference", search="_search_reference"
    )

    @api.depends("field_id")
    def _calc_value(self):
        for record in self:
            field_models = record.field_id.mapped("model")
            if len(set(field_models)) != 1:
                raise ValueError("All tracking value should belong to the same model.")
            TrackedModel = self.env[field_models[0]]
            tracked_fields = TrackedModel.fields_get(
                self.field_id.mapped("name"), attributes={"string", "type"}
            )
            fields_col_info = (
                tracked_fields.get(tracking.field_id.name)
                or {
                    "string": tracking.field_info["desc"],
                    "type": tracking.field_info["type"],
                }
                for tracking in record
            )
            if fields_col_info["type"] == "date":
                format_value = lambda value: self.env[
                    "ir.qweb.field.date"
                ].value_to_html(value, {})
            elif fields_col_info["type"] == "datetime":
                format_value = lambda value: self.env[
                    "ir.qweb.field.datetime"
                ].value_to_html(value, {})
            else:
                format_value = lambda value: value

            record.old_value = format_value(record.get_old_display_value()[0])
            record.new_value = format_value(record.get_new_display_value()[0])

    @api.depends("mail_message_id")
    def _compute_reference(self):
        for record in self:
            record.reference = "%s,%s" % (
                record.mail_message_id.model,
                record.mail_message_id.res_id,
            )

    def _search_reference(self, operator, value):
        assert operator == "="
        model, record_id = value.split(",")
        message_ids = self.env["mail.message"].search(
            [("model", "=", model), ("res_id", "=", record_id)]
        )
        return [("mail_message_id", "in", message_ids.ids)]
