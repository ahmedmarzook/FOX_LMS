"""
Created on Mar 27, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields, api


class IrModel(models.Model):
    _inherit = "ir.model"

    @api.model
    def _default_field_id(self):
        if self._context.get("default_parent_approval_model_id"):
            approval_model = self.env["approval.model"].browse(
                self._context.get("default_parent_approval_model_id")
            )
            return [
                (
                    0,
                    0,
                    {
                        "name": self.env[approval_model.model]._table + "_id",
                        "field_description": approval_model.name,
                        "ttype": "many2one",
                        "relation": approval_model.model,
                        "required": True,
                        "on_delete": "cascade",
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "x_name",
                        "field_description": "Name",
                        "ttype": "char",
                        "required": True,
                    },
                ),
            ]

        return super(IrModel, self)._default_field_id()

    field_id = fields.One2many(default=_default_field_id)
    is_approval_model = fields.Boolean()

    parent_approval_model_id = fields.Many2one("approval.model")

    def _reflect_model_params(self, model):
        vals = super(IrModel, self)._reflect_model_params(model)
        vals["is_approval_model"] = issubclass(type(model), self.pool["approval.doc"])
        return vals

    @api.model
    def _instanciate(self, model_data):
        model_class = super(IrModel, self)._instanciate(model_data)
        if model_data.get("is_approval_model") and model_class._name != "approval.doc":
            model_class._inherit = ["approval.doc"]
        return model_class

    @api.model_create_multi
    def create(self, vals_list):
        records = super(IrModel, self).create(vals_list)
        for record in records:
            if record.parent_approval_model_id:
                self.field_id.create(
                    {
                        "name": "%s_ids" % self.env[record.model]._table,
                        "model_id": record.parent_approval_model_id.model_id.id,
                        "relation": record.model,
                        "ttype": "one2many",
                        "relation_field": "%s_id"
                        % self.env[record.parent_approval_model_id.model]._table,
                    }
                )
        return records
