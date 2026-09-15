from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    chatter_position = fields.Selection(
        [("bottom", "Bottom"), ("sided", "Sided")],
        string="Chatter Position",
        default="sided",
    )
    dark_mode = fields.Boolean(string="Dark Mode", default=False)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            "chatter_position",
            "dark_mode",
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            "chatter_position",
            "dark_mode",
        ]
