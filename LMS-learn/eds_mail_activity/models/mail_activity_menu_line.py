"""
Created on Jan 10, 2022

@author: Zuhair Hammadi
"""

from odoo import models, fields, api


class MailActivityMenuLine(models.Model):
    _name = "mail.activity.menu.line"
    _order = "sequence,id"

    activity_menu_id = fields.Many2one("mail.activity.menu", ondelete="cascade")
    model_id = fields.Many2one(related="activity_menu_id.model_id", store=True)
    sequence = fields.Integer()
    menu_sequence = fields.Integer(related="activity_menu_id.sequence", store=True)
    name = fields.Char(required=True, translate=True)
    icon = fields.Binary()
    action_id = fields.Many2one("ir.actions.act_window")

    main_menu_id = fields.Many2one("ir.ui.menu", domain=[("parent_id", "=", False)])

    _sql_constraints = [
        ("name_uniq", "unique (activity_menu_id,name)", "The name should be unique !")
    ]

    @api.onchange("action_id")
    def _onchange_action_id(self):
        if self.action_id:
            menu_ids = self.env["ir.ui.menu"].search(
                [("action", "=", "%s,%d" % (self.action_id._name, self.action_id.id))]
            )
            main_menu_id = menu_ids.sorted()[:1]
            while main_menu_id.parent_id:
                main_menu_id = main_menu_id.parent_id
            self.main_menu_id = main_menu_id
