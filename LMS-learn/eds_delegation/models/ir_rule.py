"""
Created on Dec 25, 2016

@author: zuhair
"""

from odoo import models, fields, tools, api
import logging
from collections import defaultdict
from odoo.tools.safe_eval import safe_eval
from odoo.tools import config

_logger = logging.getLogger(__name__)


class Rule(models.Model):
    _inherit = "ir.rule"

    @api.model
    def _get_domain(self, domain):
        eval_context = self._eval_context()
        if domain:
            return fields.Domain(safe_eval(domain, eval_context))
        else:
            return fields.Domain([])

    def _get_delegation(self):
        if self.env.uid:
            # delegation
            self.env.cr.execute(
                """
                select delegation_line.group_id, delegation.user_id
                from delegation
                inner join delegation_line on delegation_line.delegation_id = delegation.id
                where delegation.state = 'confirmed'
                and %s between delegation.date_from and delegation.date_to
                and delegation_line.user_id = %s
                and delegation_line.active
            """,
                (fields.Date.today(), self.env.uid),
            )

            delegation = defaultdict(list)

            for group_id, user_id in self.env.cr.fetchall():
                delegation[group_id].append(user_id)
        else:
            delegation = {}

        if config.get("restricted_access"):
            for group_id in list(delegation.keys()):
                group = self.env["res.groups"].sudo().browse(group_id)
                if not group.restricted_access:
                    delegation.pop(group_id)

        return delegation

    def _make_access_error(self, operation, records):
        res = super(Rule, self)._make_access_error(operation, records)
        _logger.info(
            "Computed domain for operation %s, on model: %s, for user uid: %s, is %s",
            operation,
            self._uid,
            records._name,
            self._compute_domain(records._name, operation),
        )
        return res

    @api.model
    @tools.conditional(
        "xml" not in config["dev_mode"],
        tools.ormcache(
            "self.env.uid",
            "self.env.su",
            "model_name",
            "mode",
            "tuple(self._compute_domain_context_values())",
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        if mode not in self._MODES:
            raise ValueError("Invalid mode: %r" % (mode,))

        if self.env.su:
            return

        query = """SELECT r.id 
                    FROM ir_rule r 
                    INNER JOIN ir_model m ON (r.model_id=m.id AND m.model=%s)
                    WHERE r.active 
                    AND r.perm_{mode}
                """.format(
            mode=mode
        )

        self.env.cr.execute(query, (model_name,))
        rule_ids = [row[0] for row in self.env.cr.fetchall()]
        if not rule_ids:
            return fields.Domain([])

        delegation = self._get_delegation()

        # browse user and rules as SUPERUSER_ID to avoid access errors!
        user = self.env.user
        global_domains = []  # list of domains
        group_domains = []  # list of domains

        group_user = self.env.ref("base.group_user")

        for rule in self.sudo().browse(rule_ids):

            def domain(user_id):
                dom = self.with_user(user_id)._get_domain(rule.domain_force)
                return fields.Domain(dom)

            # Use all_group_ids (direct + implied) since in Odoo 19 group_ids only stores direct groups
            user_groups_id = user.all_group_ids
            if config.get("restricted_access"):
                user_groups_id = user_groups_id.filtered("restricted_access")

            if rule.groups & user_groups_id:
                group_domains.append(domain(user.id))
            if not rule.groups:
                global_domains.append(domain(user.id))

            for group_id, user_ids in delegation.items():
                group = self.env["res.groups"].sudo().browse(group_id)
                if (group & rule.groups) or (
                    (group.all_implied_ids - group_user) & rule.groups
                ):
                    for user_id in user_ids:
                        group_domains.append(domain(user_id))

        # combine global domains and group domains
        if not group_domains:
            return fields.Domain.AND(global_domains)
        return fields.Domain.AND(global_domains + [fields.Domain.OR(group_domains)])
