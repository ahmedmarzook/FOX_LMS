from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    theme_menu_style = fields.Selection(
        [("sidemenu", "Side Menu"), ("apps", "Top Menu")],
        string="Menu Style",
        default="apps",
    )
    theme_font_name = fields.Selection(
        [
            ("Rubik", "Rubik"),
            ("sans-serif", "Sans Serif"),
            ("poppins", "Poppins"),
            ("lato", "Lato"),
            ("merriweather", "Merriweather"),
            ("montserrat", "Montserrat"),
            ("opensans", "Open Sans"),
            ("playfairdisplay", "Playfair Display"),
            ("google-font", "Google Font"),
        ],
        string="Theme Font",
        default="Rubik",
    )
    google_font = fields.Char(string="Google Font", default="Roboto")
    theme_color_brand = fields.Char(string="Brand Color", default="#424242")
    theme_background_color = fields.Char(
        string="Background Color", default="#f2f7fb"
    )
    theme_sidebar_color = fields.Char(
        string="Sidebar Color", default="#212529"
    )
    dashboard_background = fields.Binary(
        string="Dashboard Background", attachment=True
    )
