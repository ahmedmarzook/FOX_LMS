"""
Created on Dec 22, 2016

@author: zuhair
"""

from odoo import models, fields, api, tools
import logging
from odoo.tools.config import config

_logger = logging.getLogger(__name__)


class User(models.Model):
    _inherit = "res.users"

    delegation_ids = fields.Many2many(
        "delegation.line",
        compute="_calc_delegation",
        string="Active Delegation",
        compute_sudo=True,
    )
    has_delegation = fields.Boolean(compute="_calc_delegation", compute_sudo=True)
    active_groups_ids = fields.Many2many(
        "res.groups", compute="_calc_delegation", compute_sudo=True
    )

    delegated_user_ids = fields.Many2many(
        "res.users",
        compute="_calc_delegated_user_ids",
        search="_search_delegated_user_ids",
        compute_sudo=True,
    )

    delegator_user_ids = fields.Many2many(
        "res.users",
        compute="_calc_delegator_user_ids",
        search="_search_delegator_user_ids",
        compute_sudo=True,
    )

    active_groups_count = fields.Integer(
        compute="_calc_groups_count", compute_sudo=True
    )
    groups_count = fields.Integer(compute="_calc_groups_count", compute_sudo=True)

    @api.depends("active_groups_ids", "group_ids")
    def _calc_groups_count(self):
        for record in self:
            record.active_groups_count = len(record.active_groups_ids)
            record.groups_count = len(record.group_ids)

    @api.model
    def _context_groups_ids(self):
        roles = filter(None, self._context.get("delegation_roles", "").split(","))
        group_ids = [self.env.ref(group).id for group in roles] + self._context.get(
            "delegation_roles_ids", []
        )
        return group_ids

    @api.depends("all_group_ids")
    def _calc_delegation(self):
        DelegationLine = self.env["delegation.line"].sudo()
        for record in self:
            # Only query delegations for real (DB-stored) records.
            # Virtual records (NewId) arise during onchange — including their delegated
            # groups in active_groups_ids would cause _compute_role to return a wrong
            # role (e.g. 'group_system' from a delegation), triggering _onchange_role
            # which reverts the group_ids the user just edited.
            if isinstance(record.id, int):
                delegation_ids = DelegationLine.get([("user_id", "=", record.id)])
            else:
                delegation_ids = DelegationLine
            record.delegation_ids = delegation_ids
            record.has_delegation = bool(delegation_ids)
            delegation_groups_ids = delegation_ids.mapped("group_id")
            active_groups_ids = (
                record.all_group_ids
                | delegation_groups_ids
                | delegation_groups_ids.mapped("all_implied_ids")
            )
            if config.get("restricted_access"):
                active_groups_ids = active_groups_ids.filtered("restricted_access")
            record.active_groups_ids = active_groups_ids

    def _calc_delegated_user_ids(self):
        group_ids = self._context_groups_ids()
        for record in self:
            if not isinstance(record.id, int):
                record.delegated_user_ids = self.env["delegation.line"]
                continue
            delegation_ids = self.env["delegation.line"].get(
                [("delegator_user_id", "=", record.id), ("group_id", "in", group_ids)]
            )
            record.delegated_user_ids = delegation_ids.mapped("user_id")

    @api.model
    def _search_delegated_user_ids(self, operator, value):
        group_ids = self._context_groups_ids()
        user_ids = self.search_fetch([("id", operator, value)], ["id"])
        delegation_ids = self.env["delegation.line"].get(
            [("user_id", "in", user_ids.ids), ("group_id", "in", group_ids)]
        )
        return [("id", "in", delegation_ids.mapped("delegator_user_id"))]

    def _calc_delegator_user_ids(self):
        group_ids = self._context_groups_ids()
        for record in self:
            if not isinstance(record.id, int):
                record.delegator_user_ids = self.env["delegation.line"]
                continue
            delegation_ids = self.env["delegation.line"].get(
                [("user_id", "=", record.id), ("group_id", "in", group_ids)]
            )
            record.delegator_user_ids = delegation_ids.mapped("delegator_user_id")

    @api.model
    def _search_delegator_user_ids(self, operator, value):
        group_ids = self._context_groups_ids()
        user_ids = self.search_fetch([("id", operator, value)], ["id"])
        delegation_ids = self.env["delegation.line"].get(
            [("delegator_user_id", "in", user_ids.ids), ("group_id", "in", group_ids)]
        )
        return [("id", "in", delegation_ids.mapped("user_id"))]

    @api.depends("group_ids")
    def _compute_role(self):
        """Override to compute role from actual groups only, not delegated groups.

        Without this override, the parent calls has_group() which goes through
        our _has_group() override and uses active_groups_ids (which includes
        delegated groups). For a user with a delegation granting group_system,
        this incorrectly returns role='group_system', causing _onchange_role to
        fire and revert the user's group_ids changes.
        """
        group_system = self.env.ref("base.group_system")
        group_user = self.env.ref("base.group_user")
        for user in self:
            ids = user.all_group_ids._ids
            user.role = (
                "group_system" if group_system.id in ids else
                "group_user" if group_user.id in ids else
                False
            )

    def _has_group(self, group_ext_id):
        """Checks whether user belongs to given group, including delegated groups.

        :param str group_ext_id: external ID (XML ID) of the group.
           Must be provided in fully-qualified form (``module.ext_id``), as there
           is no implicit module to use..
        :return: True if the current user is a member of the group with the
           given external ID (XML ID), else False.
        """
        group = self.env.ref(group_ext_id, False)
        if not group:
            return False
        # Use active_groups_ids (includes delegated groups + implied groups) for self,
        # falling back to all_group_ids (direct + implied). In Odoo 19, group_ids only
        # stores direct groups; all_group_ids includes implied groups.
        # NOTE: Use group.id in group_ids.ids instead of 'group in group_ids' because
        # Odoo virtual records (used during onchange) have a broken __contains__ for
        # many2many fields — the 'in' operator returns False even when the ID is present.
        group_ids = self.active_groups_ids or self.all_group_ids
        return group.id in group_ids.ids
