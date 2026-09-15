"""
Created on Jun 5, 2018

@author: Zuhair Hammadi
"""

from odoo import models, api
import ast


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model_create_multi
    def create(self, vals_list):
        records = super(Base, self).create(vals_list)
        for record, vals in zip(records, vals_list):
            self.env["validation"]._dynamic_validation(record, "on_create", vals)
        return records

    def _write(self, vals):
        self.env["validation"]._dynamic_validation(self, "be_write", vals)
        res = super(Base, self)._write(vals)
        self.env["validation"]._dynamic_validation(self, "on_write", vals)
        return res

    def unlink(self):
        self.env["validation"]._dynamic_validation(self, "on_unlink")
        return super(Base, self).unlink()

    def _match_domain(self, domain):
        if isinstance(domain, str):
            domain = ast.literal_eval(domain)
        if not domain:
            return True
        domain = [("id", "=", self.id)] + domain
        return bool(self.with_context(active_test=False).search(domain, count=True))
