"""
Created on Jan 10, 2022

@author: Zuhair Hammadi
"""

from odoo import models, fields


class MailActivityMenu(models.Model):
    _name = "mail.activity.menu"
    _order = "sequence,id"
    _rec_name = "model_id"

    model_id = fields.Many2one(
        "ir.model",
        required=True,
        ondelete="cascade",
        string="Object",
        domain=[("is_mail_activity", "=", True)],
    )
    model = fields.Char(related="model_id.model")
    sequence = fields.Integer()
    line_ids = fields.One2many("mail.activity.menu.line", "activity_menu_id")
    active = fields.Boolean(default=True)

    code = fields.Text("Python Code")

    _sql_constraints = [
        ("model_uniq", "unique (model_id)", "The model should be unique !")
    ]

    def compute_activity_type(self):
        MailActivity = self.env["mail.activity"]
        activities = MailActivity.search([("res_model_id", "=", self.model_id.id)])
        self.env.add_to_compute(MailActivity._fields["res_type"], activities)
        activities.env.cr.flush()
