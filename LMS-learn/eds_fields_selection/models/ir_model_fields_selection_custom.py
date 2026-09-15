"""
Created on Feb 19, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields, api, tools


class IrModelFieldSelectionCustom(models.Model):
    _name = "ir.model.fields.selection.custom"
    _description = "Field Selection"
    _order = "sequence,id"

    def _get_sequence(self):
        self.env.cr.execute(f"select max(sequence) from {self._table}")
        (sequence,) = self.env.cr.fetchone()
        return (sequence or 0) + 1

    field_id = fields.Many2one("ir.model.fields", required=True, ondelete="cascade")
    value = fields.Char(required=True)
    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=_get_sequence)

    _sql_constraints = [
        ("uk_value", "unique(field_id, value)", "Value must be unique!")
    ]

    def name_get(self):
        res = []
        for record in self:
            res.append(
                (
                    record.id,
                    "%s.%s - %s"
                    % (record.field_id.model, record.field_id.name, record.value),
                )
            )
        return res

    @api.model
    @tools.ormcache("field_id", "self.env.lang")
    def _get_selection(self, field_id):

        if field_id not in self._get_custom_fields_selection():
            return

        self._flush(["value", "name"])

        records = self.sudo().search([
            ("field_id", "=", field_id),
            ("active", "=", True)
        ])

        return [(record.value, record.name) for record in records]

    @api.model
    @tools.ormcache()
    def _get_custom_fields_selection(self):
        cr = self.env.cr
        cr.execute("""
                   SELECT DISTINCT field_id
                   FROM ir_model_fields_selection_custom
                   WHERE active = true
                   """)
        return {row[0] for row in cr.fetchall()}

    @api.model_create_multi
    def create(self, vals_list):
        res = super(IrModelFieldSelectionCustom, self).create(vals_list)
        self.env.registry.clear_cache()
        return res

    def unlink(self):
        res = super(IrModelFieldSelectionCustom, self).unlink()
        self.env.registry.clear_cache()
        return res

    def write(self, vals):
        res = super(IrModelFieldSelectionCustom, self).write(vals)
        self.env.registry.clear_cache()
        return res
