# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details

from odoo import models, fields, api


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def _load_menus_blacklist(self):
        res = super()._load_menus_blacklist()
        if not self.env.user._smart_show_edit_mode():
            res.append(self.env.ref("eds_smart_theme.menu_theme_configurator").id)
        return res

    icon_img = fields.Image("Menu New Image")
    use_icon = fields.Boolean("Use Icon")
    icon_class_name = fields.Char("Icon Class Name")
    spiffy_app_group_id = fields.Many2one("spiffy.app.group", name="Smart App Group")
    spiffy_app_group = fields.Char("Smart App Groups")
    app_menu_list = fields.Char("Smart App Groups List")
