"""
Created on Dec 22, 2016

@author: zuhair
"""

from odoo import models, api, tools
import logging

_logger = logging.getLogger(__name__)


class Menu(models.Model):
    _inherit = "ir.ui.menu"

    @api.model
    @tools.ormcache("frozenset(self.env.user.active_groups_ids.ids)", "debug")
    def _visible_menu_ids(self, debug=False):
        """Return the ids of the menu items visible to the user."""
        # retrieve all menus, and determine which ones are visible
        context = {"ir.ui.menu.full_list": True}
        menus = self.with_context(context).search([])

        groups = self.env.user.active_groups_ids
        if not debug:
            groups = groups - self.env.ref("base.group_no_one")
        # first discard all menus with groups the user does not have
        menus = menus.filtered(
            lambda menu: not menu.group_ids or menu.group_ids & groups
        )

        # take apart menus that have an action
        action_menus = menus.filtered(lambda m: m.action and m.action.exists())
        folder_menus = menus.filtered("child_id")
        visible = self.browse()

        # process action menus, check whether their action is allowed
        access = self.env["ir.model.access"]
        MODEL_GETTER = {
            "ir.actions.act_window": lambda action: action.res_model,
            "ir.actions.report": lambda action: action.model,
            "ir.actions.server": lambda action: action.model_id.model,
        }

        def has_folder_access(menu):
            menu = menu.parent_id
            while menu:
                if menu not in folder_menus:
                    return False
                menu = menu.parent_id
            return True

        for menu in action_menus:
            get_model = MODEL_GETTER.get(menu.action._name)
            if (
                not get_model
                or not get_model(menu.action)
                or access.check(get_model(menu.action), "read", False)
            ):
                if not has_folder_access(menu):
                    continue
                # make menu visible, and its folder ancestors, too
                visible += menu
                menu = menu.parent_id
                while menu and menu in folder_menus and menu not in visible:
                    visible += menu
                    menu = menu.parent_id

        return set(visible.ids)
