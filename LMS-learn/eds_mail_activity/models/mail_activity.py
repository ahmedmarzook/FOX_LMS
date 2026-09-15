"""
Created on Jan 10, 2022

@author: Zuhair Hammadi
"""

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


class MailActivity(models.Model):
    _inherit = "mail.activity"

    res_type = fields.Char(
        string="Related Document Type", compute="_calc_res_type", store=True
    )

    @api.depends("res_model_id", "res_id")
    def _calc_res_type(self):
        for activity in self:
            separation_id = self.env["mail.activity.menu"].search(
                [("model_id", "=", activity.res_model_id.id)]
            )
            if separation_id.code:
                record = self.env[activity.res_model].browse(activity.res_id)

                localdict = self.env["ir.actions.actions"]._get_eval_context()
                localdict.update(
                    {
                        "self": record,
                        "record": record,
                        "env": self.env,
                        "activity": activity,
                    }
                )
                safe_eval(separation_id.code, localdict, mode="exec", nocopy=True)
                activity.res_type = localdict.get("result")

            else:
                activity.res_type = False
