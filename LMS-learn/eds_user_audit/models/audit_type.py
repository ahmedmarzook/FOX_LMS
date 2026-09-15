"""
Created on Sep 6, 2018

@author: Zuhair Hammadi
"""

from odoo import models, fields


class AuditType(models.Model):
    _name = "audit.type"
    _description = "audit.type"

    name = fields.Char(required=True)
    value = fields.Integer(required=True)

    _sql_constraints = [
        ("uk_name", "unique(name)", "Name should be unique!"),
        ("uk_value", "unique(value)", "Value should be unique!"),
    ]
