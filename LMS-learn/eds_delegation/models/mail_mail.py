"""
Created on Mar 7, 2017

@author: Zuhair Hammadi
"""

from odoo import models, api


class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            template_id = vals.pop("template_id", False)
            if template_id:
                self.env["mail.template"].browse(int(template_id)).add_delegation_email(
                    vals
                )
        return super(MailMail, self).create(vals_list)
