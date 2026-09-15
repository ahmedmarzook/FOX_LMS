"""
Created on Dec 25, 2016

@author: zuhair
"""

from odoo import models, api, tools
import logging
from odoo.tools import config
from lxml import etree  # @UnresolvedImport
from lxml.builder import E

# from odoo.addons.base.models.ir_ui_view import INHERIT_ORDER

_logger = logging.getLogger(__name__)


class View(models.Model):
    _inherit = "ir.ui.view"

    # @api.model
    # def get_inheriting_views_arch(self, view_id, model):
    #     """Retrieves the architecture of views that inherit from the given view, from the sets of
    #        views that should currently be used in the system. During the module upgrade phase it
    #        may happen that a view is present in the database but the fields it relies on are not
    #        fully loaded yet. This method only considers views that belong to modules whose code
    #        is already loaded. Custom views defined directly in the database are loaded only
    #        after the module initialization phase is completely finished.
    #
    #        :param int view_id: id of the view whose inheriting views should be retrieved
    #        :param str model: model identifier of the inheriting views.
    #        :rtype: list of tuples
    #        :return: [(view_arch,view_id), ...]
    #     """
    #     user_groups = self.env.user.active_groups_ids
    #     conditions = self._get_inheriting_views_arch_domain(view_id, model)
    #
    #     if self.pool._init and not self._context.get('load_all_views'):
    #         # Module init currently in progress, only consider views from
    #         # modules whose code is already loaded
    #
    #         # Search terms inside an OR branch in a domain
    #         # cannot currently use relationships that are
    #         # not required. The root cause is the INNER JOIN
    #         # used to implement it.
    #         modules = tuple(self.pool._init_modules) + (self._context.get('install_module'),)
    #         views = self.search(conditions + [('model_ids.module', 'in', modules)])
    #         views_cond = [('id', 'in', list(self._context.get('check_view_ids') or (0,)) + views.ids)]
    #         views = self.search(conditions + views_cond, order=INHERIT_ORDER)
    #     else:
    #         views = self.search(conditions, order=INHERIT_ORDER)
    #
    #     return [(view.arch, view.id)
    #             for view in views.sudo()
    #             if not view.group_ids or (view.group_ids & user_groups)]

    # apply ormcache_context decorator unless in dev mode...


@api.model
@tools.conditional(
    "xml" not in config["dev_mode"],
    tools.ormcache(
        "frozenset(self.env.user.active_groups_ids.ids)",
        "view_id",
        "tuple(self._context.get(k) for k in self._read_template_keys())",
    ),
)
def _read_template(self, view_id):
    arch = self.browse(view_id).get_combined_arch()  # Updated method
    arch_tree = etree.fromstring(arch)
    self.distribute_branding(arch_tree)
    arch = etree.tostring(arch_tree, encoding="unicode")
    return arch
