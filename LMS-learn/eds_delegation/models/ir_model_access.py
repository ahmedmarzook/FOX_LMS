"""
Created on Dec 22, 2016

@author: zuhair
"""

from odoo import models, tools, api, _
from odoo.tools import SQL

import logging
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class ModelAccess(models.Model):
    _inherit = "ir.model.access"

    @api.model
    def check_groups(self, group):
        """Check whether the current user has the given group."""
        group_ids = self.env.user.active_groups_ids or self.env.user.all_group_ids
        return self.env.ref(group) in group_ids

    @tools.ormcache("self.env.uid", "frozenset(self.env.user.active_groups_ids._ids)", "mode")
    def _get_allowed_models(self, mode="read"):
        assert mode in ("read", "write", "create", "unlink"), "Invalid access mode"

        # Use active_groups_ids (includes delegated groups), falling back to _get_group_ids
        active_groups = self.env.user.active_groups_ids
        group_ids = tuple(active_groups._ids) if active_groups else self.env.user._get_group_ids()

        self.flush_model()
        rows = self.env.execute_query(SQL("""
            SELECT m.model
              FROM ir_model_access a
              JOIN ir_model m ON (m.id = a.model_id)
             WHERE a.perm_%s
               AND a.active
               AND (
                    a.group_id IS NULL OR
                    a.group_id IN %s
                )
            GROUP BY m.model
        """, SQL(mode), group_ids or (None,)))

        return frozenset(v[0] for v in rows)
