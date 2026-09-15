from odoo import fields, models


class SmartPortalQuickLink(models.Model):
    _name = "smart.portal.quick.link"
    _description = "Smart portal quick link"
    _order = "sequence, id"

    name = fields.Char(string="Name", required=True, translate=True)
    icon = fields.Char(
        string="Icon",
        default="🔗",
        help="Short label shown on the card (e.g. emoji or 1–2 characters).",
    )
    link_url = fields.Char(
        string="Link",
        required=True,
        help="URL or path: full https://… or internal paths such as /web#action=…",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
