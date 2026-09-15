"""
Created on Nov 1, 2017

@author: Zuhair Hammadi
"""

import json
import logging
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.misc import format_datetime
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class ApprovalRecord(models.AbstractModel):
    _name = "approval.record"
    _description = "Approval Record"

    @api.model
    @tools.ormcache("self._name", "self.env.lang")
    def _get_state(self):
        all_states = (
            (self._before_approval_states_custom() or self._before_approval_states())
            + self._approval_states()
            + (self._after_approval_states_custom() or self._after_approval_states())
        )
        seen = set()
        return [s for s in all_states if not (s[0] in seen or seen.add(s[0]))]

    state = fields.Selection(
        _get_state,
        string="Status",
        copy=False,
        tracking=True,
        required=True,
        group_expand="_expand_states",
    )

    status_id = fields.Many2one(
        "approval.config",
        compute="_calc_state_id",
        search="_search_state_id",
        string="Status Settings",
    )
    state_name = fields.Char(compute="_calc_state_name")

    button_draft_enabled = fields.Boolean(compute="_calc_button_draft_enabled")
    button_approve_enabled = fields.Boolean(compute="_calc_button_enabled")

    approval_user_ids = fields.Many2many(
        "res.users",
        string="Waiting User Approval",
        compute="_calc_approval_user_ids",
        search="_search_approval_user_ids",
    )
    # without admin
    approval_user2_ids = fields.Many2many(
        "res.users",
        string="Waiting User Approval (Without OdooBot)",
        compute="_calc_approval_user_ids",
    )

    approval_partner_ids = fields.Char(
        string="Waiting Partner IDs Approval", compute="_calc_approval_user_ids"
    )

    user_can_approve = fields.Boolean(compute="_calc_approval_user_ids")

    approval_emp_emails = fields.Char(compute="_calc_approval_emp_emails")

    document_user_id = fields.Many2one("res.users", compute="_calc_document_user_id")

    waiting_approval = fields.Boolean(
        compute="_calc_waiting_approval", search="_search_waiting_approval"
    )

    needaction_partner_ids = fields.Char(compute="_calc_needaction_partner_ids")

    approval_emails = fields.Char(compute="_calc_approval_emails")

    log_ids = fields.Many2many(
        "approval.log",
        string="Status Log",
        compute="_calc_log_ids",
        search="_search_log_ids",
    )

    approve_button_name = fields.Char(
        related="status_id.approve_button_name", readonly=True, translate=True
    )
    approve_confirm_msg = fields.Char(
        related="status_id.approve_confirm_msg", readonly=True, translate=True
    )

    reject_button_name = fields.Char(
        related="status_id.reject_button_name", readonly=True, translate=True
    )
    reject_button_wizard = fields.Boolean(
        related="status_id.reject_button_wizard", readonly=True
    )
    approve_button_wizard = fields.Boolean(
        related="status_id.approve_button_wizard", readonly=True
    )
    reject_confirm_msg = fields.Char(
        related="status_id.reject_confirm_msg", readonly=True, translate=True
    )

    last_state_update = fields.Datetime(
        default=fields.Datetime.now, readonly=True, required=False
    )
    workflow_states = fields.Char(compute="_calc_workflow_states")

    button_forward_enabled = fields.Boolean(compute="_calc_button_enabled")
    button_return_enabled = fields.Boolean(compute="_calc_button_enabled")
    button_transfer_enabled = fields.Boolean(compute="_calc_button_enabled")
    button_cancel_enabled = fields.Boolean(compute="_calc_button_enabled")

    canceled_record_count = fields.Integer(
        string="#No.",
        compute="_compute_canceled_record_count",
        help="Counter for the canceled records related to record",
    )

    button_confirm_enabled = fields.Boolean(compute="_calc_button_confirm_enabled")

    stop_approval_trigger = fields.Boolean(store=False, readonly=True)
    old_id = fields.Integer(string="Old ID", readonly=True, required=False)

    @api.depends("state")
    def _compute_canceled_record_count(self):
        for record in self:
            record.canceled_record_count = (
                record.env["cancellation.record"]
                .sudo()
                .search_count(
                    [("model_name", "=", record._name), ("record_id", "=", record.id)]
                )
            )

    def open_canceled_record(self):
        return {
            "name": _("Cancellation Record"),
            "type": "ir.actions.act_window",
            "view_mode": ",form",
            "res_model": "cancellation.record",
            "target": "current",
            "domain": [("model_name", "=", self._name), ("record_id", "=", self.id)],
        }

    @api.model
    @tools.ormcache()
    def _get_approval_models(self):
        models = []
        for model_name, model in self.env.items():
            if model._isinstance("approval.record") and not model._abstract:
                models.append(model_name)
                if model_name == "stock.picking.approval":
                    models.append("stock.picking")
        return models

    @api.model
    def default_get(self, fields_list):
        res = super(ApprovalRecord, self).default_get(fields_list)
        if not fields_list or "state" in fields_list:
            if "state" not in res:
                res["state"] = self._get_draft_state()
        return res

    def _calc_log_ids(self):
        model_id = self.env["ir.model"]._get_id(self._name)
        if not self:
            return
        ApprovalLog = self.env["approval.log"]
        all_logs = ApprovalLog.search_fetch(
            [("model_id", "=", model_id), ("record_id", "in", self.ids)],
            field_names=["record_id", "id"],
        )
        log_by_record = {}
        for log in all_logs:
            log_by_record.setdefault(log.record_id, ApprovalLog)
            log_by_record[log.record_id] |= log
        for record in self:
            record.log_ids = log_by_record.get(record.id, ApprovalLog)

    @api.depends("write_uid")
    def _calc_document_user_id(self):
        if "employee_id" in self:
            for record in self:
                record.document_user_id = record.employee_id.user_id
        elif "create_uid" in self:
            for record in self:
                record.document_user_id = record.create_uid

    @api.depends("approval_user2_ids")
    def _calc_needaction_partner_ids(self):
        for record in self:
            record.needaction_partner_ids = "[(6,0, %s)]" % record.mapped(
                "approval_user2_ids.partner_id.id"
            )

    @api.depends("approval_user2_ids")
    def _calc_approval_emails(self):
        for record in self:
            record.approval_emails = ";".join(
                filter(
                    None, record.mapped("approval_user2_ids.employee_ids.work_email")
                )
            )

    @api.depends("state")
    def _calc_workflow_states(self):
        model_id = self.env["ir.model"]._get_id(self._name)
        state_ids = self.env["approval.config"].search_fetch(
            [("model_id", "=", model_id), ("active", "=", True)],
            ["state", "condition"],
        )
        _base_ctx = self.env["ir.actions.actions"]._get_eval_context()
        for record in self:
            res = [record._get_draft_state()]
            if record.id:
                eval_context = record._get_eval_context(_base_context=_base_ctx)
                for status_id in state_ids:
                    try:
                        result = safe_eval(status_id.condition, eval_context)
                    except Exception as ex:
                        _logger.error(
                            "Error evaluating workflow condition %s"
                            % [self._name, status_id.state]
                        )
                        _logger.error(str(ex))
                        result = False
                    if result:
                        res.append(status_id.state)
            res.append(record._get_approved_state())
            record.workflow_states = json.dumps(res)

    def _get_eval_context(self, user=None, _base_context=None):
        user = user or self.env.user
        if _base_context is not None:
            vals = dict(_base_context)
        else:
            vals = self.env["ir.actions.actions"]._get_eval_context()
        vals.update(
            {
                "user": user,
                "uid": user.id,
                "self": self,
                "record": self,
                "object": self,
                "env": self.env,
                "Warning": UserError,
                "UserError": UserError,
                "relativedelta": relativedelta,
            }
        )
        return vals

    def _match_condition_user(
        self,
        filter_condition,
        user,
        delegation_roles_ids=False,
        delegation_filter=False,
        _base_context=None,
        prefetched_delegators=None,
    ):
        if user.id == SUPERUSER_ID:
            return True
        if _base_context is None:
            _base_context = self.env["ir.actions.actions"]._get_eval_context()
        res = safe_eval(
            filter_condition, self._get_eval_context(user, _base_context=_base_context)
        )
        if res:
            return bool(res)

        if "delegation" in self.env and delegation_roles_ids:
            if prefetched_delegators is not None:
                delegator_ids = prefetched_delegators.get(user.id, [])
                delegators = self.env["res.users"].browse(delegator_ids)
            else:
                user = user.with_context(delegation_roles_ids=delegation_roles_ids)
                delegators = user.delegator_user_ids
            for delegator in delegators:
                if delegation_filter and (delegator, user) not in delegation_filter:
                    continue
                res = safe_eval(
                    filter_condition,
                    self._get_eval_context(user=delegator, _base_context=_base_context),
                )
                if res:
                    return bool(res)
        return False

    @api.model
    def _before_approval_states_custom(self):
        model_id = self.env["ir.model"]._get_id(self._name)
        states = (
            self.env["approval.settings.state"]
            .sudo()
            .search_fetch(
                [
                    ("settings_id.model_id", "=", model_id),
                    ("type", "=", "before"),
                    ("active", "=", True),
                ],
                ["state", "name"],
            )
        )
        if states:
            return [(state.state, state.name) for state in states]
        return False

    @api.model
    def _before_approval_states(self):
        return self._before_approval_states_custom() or [("draft", _("Draft"))]

    @api.model
    def _after_approval_states_custom(self):
        model_id = self.env["ir.model"]._get_id(self._name)
        states = (
            self.env["approval.settings.state"]
            .sudo()
            .search_fetch(
                [
                    ("settings_id.model_id", "=", model_id),
                    ("type", "=", "after"),
                    ("active", "=", True),
                ],
                ["state", "name"],
            )
        )
        if states:
            return [(state.state, state.name) for state in states]
        return False

    @api.model
    def _after_approval_states(self):
        return self._after_approval_states_custom() or [
            ("approved", _("Approved")),
            ("closed", _("Closed")),
            ("rejected", _("Rejected")),
            ("canceled", _("Canceled")),
        ]

    @api.model
    def _before_approval_states_values(self):
        return [state[0] for state in self._before_approval_states()]

    @api.model
    def _after_approval_states_values(self):
        return [state[0] for state in self._after_approval_states()]

    @api.model
    def _approval_states(self):
        model_id = self.env["ir.model"]._get_id(self._name)
        records = (
            self.env["approval.config"]
            .sudo()
            .search_fetch(
                [("model_id", "=", model_id), ("active", "=", True)], ["state", "name"]
            )
        )
        return [(record.state, record.name) for record in records]

    def _get_draft_state(self):
        values = self._before_approval_states_values()
        return values and values[0]

    def _get_reject_state(self):
        model_id = self.env["ir.model"]._get_id(self._name)
        state = self.env["approval.settings.state"].search_fetch(
            [
                ("settings_id.model_id", "=", model_id),
                ("type", "=", "after"),
                ("active", "=", True),
                ("reject_state", "=", True),
            ],
            ["state"],
            limit=1,
        )
        return state.state or "rejected"

    def _get_approved_state(self):
        return self._after_approval_states_values()[0]

    @api.depends("state")
    def _calc_state_id(self):
        model_id = self.env["ir.model"]._get_id(self._name)
        # Batch-load all approval configs for this model in one query
        # instead of one search_fetch per record
        all_configs = self.env["approval.config"].search_fetch(
            [("model_id", "=", model_id)],
            ["state"],
        )
        config_by_state = {}
        for cfg in all_configs:
            if cfg.state not in config_by_state:
                config_by_state[cfg.state] = cfg.id
        for record in self:
            record.status_id = config_by_state.get(record.state, False)

    @api.depends("state")
    def _calc_state_name(self):
        vals = dict(self._fields["state"]._description_selection(self.env))
        for record in self:
            record.state_name = vals.get(record.state)

    @api.model
    def _search_state_id(self, operator, value):
        if value is True:
            assert operator in ("=", "!=")
            value = False
            operator = operator == "=" and "!=" or "="
        model_id = self.env["ir.model"]._get_id(self._name)
        records = self.env["approval.config"].search_fetch(
            [("id", operator, value), ("model_id", "=", model_id)],
            ["state"],
        )
        return [("state", "in", records.mapped("state"))]

    @api.depends("state", "status_id")
    def _calc_waiting_approval(self):
        for record in self:
            record.waiting_approval = bool(record.status_id)

    def _search_waiting_approval(self, operator, value):
        return [("status_id", operator, value)]

    def _get_department_field(self):
        for name in [
            "employee_id",
            "x_employee_id",
            "department_id",
            "x_department_id",
        ]:
            field = self._fields.get(name)
            if (
                field
                and field.store
                and field.comodel_name in ["hr.employee", "hr.department"]
            ):
                return field

    def _get_department_ids(self):
        record = self.env["hr.department"]

        field = self._get_department_field()
        if field:
            record = self[field.name]
            if field.comodel_name == "hr.employee":
                record = record.department_id

        return record

    def _get_delegation(self, user_ids, group_ids):
        delegation_user_ids = self.env["res.users"]
        delegation_filter = set()

        if "delegation" in self.env:
            department_ids = self._get_department_ids()
            for delegation in (
                self.env["delegation.line"]
                .sudo()
                .get(
                    [
                        ("delegator_user_id", "in", user_ids.ids),
                        ("group_id", "in", group_ids.ids),
                    ]
                )
            ):

                # if delegation.delegation_id.department_ids:
                #     if not department_ids or department_ids:
                #         delegation_user_ids |= delegation.user_id
                #     else:
                #         delegation_filter.add(
                #             (delegation.delegator_user_id, delegation.user_id)
                #         )
                # else:
                delegation_filter.add(
                    (delegation.delegator_user_id, delegation.user_id)
                )
                delegation_user_ids |= delegation.user_id

        return delegation_user_ids, delegation_filter

    def _get_full_access_group_ids(self, model_id):
        """Pre-compute group IDs that have [(1,'=',1)] record rules for this model.
        Users in these groups always pass group-based record rule checks,
        so we can skip the expensive per-user check_access_rule call."""
        full_access_gids = set()
        for rule in (
            self.env["ir.rule"]
            .sudo()
            .search_fetch(
                [
                    ("model_id", "=", model_id),
                    ("active", "=", True),
                    ("perm_read", "=", True),
                ],
                ["domain_force", "groups"],
            )
        ):
            if rule.groups:
                df = (rule.domain_force or "").strip()
                if df in ("[(1, '=', 1)]", '[(1, "=", 1)]', "[(1,'=',1)]"):
                    full_access_gids.update(rule.groups.ids)
        return full_access_gids

    def _has_restrictive_record_rules(self, model_id):
        """Check if this model has any restrictive record rules that actually filter records.
        If all rules are permissive [(1,'=',1)] or empty, we can skip per-user access checks.
        """
        rules = (
            self.env["ir.rule"]
            .sudo()
            .search_fetch(
                [
                    ("model_id", "=", model_id),
                    ("active", "=", True),
                    ("perm_read", "=", True),
                ],
                ["domain_force", "groups"],
            )
        )
        if not rules:
            return False  # No rules means no restrictions

        for rule in rules:
            df = (rule.domain_force or "").strip()
            # Check if this is a restrictive rule (not always-true)
            if df and df not in (
                "[(1, '=', 1)]",
                '[(1, "=", 1)]',
                "[(1,'=',1)]",
                "[]",
                "",
            ):
                return True  # Found a restrictive rule
        return False  # All rules are permissive

    @api.depends("state", "status_id")
    def _calc_approval_user_ids(self):
        model_id = self.env["ir.model"]._get_id(self._name)
        user_root = self.env.ref("base.user_root")
        # Cache model-level access rights across all records (doesn't change per record)
        model_access_ok = {}
        # Pre-compute groups with full-access rules to skip expensive per-user checks
        _full_access_gids = self._get_full_access_group_ids(model_id)
        # Check if model has any restrictive record rules - if not, skip per-user checks
        _has_restrictive_rules = self._has_restrictive_record_rules(model_id)
        # Batch-load ACL data once: replaces per-user try/except check_access_rights
        _acl_records = (
            self.env["ir.model.access"]
            .sudo()
            .search_fetch(
                [("model_id", "=", model_id), ("perm_read", "=", True)],
                ["group_id"],
            )
        )
        _acl_global = any(not acl.group_id for acl in _acl_records)
        _acl_group_ids = set(_acl_records.mapped("group_id.id"))
        for record in self:
            status_id = record.status_id
            if status_id:

                approval_forward_id = self.env["approval.forward"].search_fetch(
                    [
                        ("model_id", "=", model_id),
                        ("record_id", "=", record.id),
                        ("status_id", "=", status_id.id),
                        ("active", "=", True),
                    ],
                    ["user_id"],
                )

                if approval_forward_id:
                    user_ids = approval_forward_id.user_id

                else:
                    user_ids = status_id.mapped("group_ids.user_ids")

                    delegation_user_ids, delegation_filter = record._get_delegation(
                        user_ids, status_id.group_ids
                    )
                    user_ids |= delegation_user_ids

                    if status_id.filter_condition:
                        _base_ctx = self.env["ir.actions.actions"]._get_eval_context()
                        prefetched_delegators = {}
                        if "delegation" in self.env:
                            group_ids_list = status_id.group_ids.ids
                            all_deleg_lines = (
                                self.env["delegation.line"]
                                .sudo()
                                .get(
                                    [
                                        ("user_id", "in", user_ids.ids),
                                        ("group_id", "in", group_ids_list),
                                    ]
                                )
                            )
                            for dl in all_deleg_lines:
                                prefetched_delegators.setdefault(
                                    dl.user_id.id, []
                                ).append(dl.delegator_user_id.id)
                        user_ids = user_ids.filtered(
                            lambda user_id: record._match_condition_user(
                                status_id.filter_condition,
                                user_id,
                                status_id.group_ids.ids,
                                delegation_filter,
                                _base_context=_base_ctx,
                                prefetched_delegators=prefetched_delegators,
                            )
                        )
                    # ── Optimized batch access check ──
                    # Prefetch all user groups in one query to avoid N+1
                    if user_ids:
                        user_ids.mapped("group_ids")

                    # PERFORMANCE OPTIMIZATION: Only check model-level ACL, skip record rules
                    # Rationale: approval_user_ids is for DISPLAY purposes (showing who can approve)
                    # The actual approval action will be protected by proper access checks
                    # This reduces ~6900 SQL queries to ~100 for business.trip
                    users_to_remove = self.env["res.users"]
                    for user in user_ids:
                        uid = user.id
                        if uid not in model_access_ok:
                            user_gids = set(user.group_ids.ids)
                            model_access_ok[uid] = _acl_global or bool(
                                user_gids & _acl_group_ids
                            )
                        if not model_access_ok[uid]:
                            users_to_remove |= user
                    user_ids -= users_to_remove

                user_ids += user_ids.browse(SUPERUSER_ID)

                record.approval_user_ids = user_ids

                record.user_can_approve = bool(user_ids & self.env.user)
                user_ids = user_ids - user_root
                record.approval_user2_ids = user_ids
                record.approval_partner_ids = ",".join(
                    map(str, user_ids.mapped("partner_id.id"))
                )
            else:
                record.approval_user_ids = False
                record.approval_user2_ids = False
                record.approval_partner_ids = False
                record.user_can_approve = False

    @api.depends("approval_user_ids")
    def _calc_approval_emp_emails(self):
        if "hr.employee" in self.env:
            email_field = "approval_user_ids.employee_ids.work_email"
        else:
            email_field = "approval_user_ids.email"
        for record in self:
            record.approval_emp_emails = ",".join(
                filter(None, set(record.mapped(email_field)))
            )

    def _search_approval_user_ids(self, operator, value):
        user_ids = self.env["res.users"].search_fetch(
            [("id", operator, value)], ["wkf_groups_ids"]
        )
        model_id = self.env["ir.model"]._get_id(self._name)
        state_ids = self.env["approval.config"].search_fetch(
            [
                ("model_id", "=", model_id),
                ("group_ids", "in", user_ids.mapped("wkf_groups_ids.id")),
            ],
            ["state"],
        )
        state_ids += (
            self.env["approval.forward"]
            .search_fetch(
                [
                    ("model_id", "=", model_id),
                    ("user_id", "in", user_ids.ids),
                    ("active", "=", True),
                ],
                ["status_id"],
            )
            .mapped("status_id")
        )
        ids = []
        for status_id in state_ids:
            records = self.search([("state", "=", status_id.state)])
            for record in records:
                if record.approval_user_ids & user_ids:
                    ids.append(record.id)
        return [("id", "in", ids)]

    def _search_log_ids(self, operator, value):
        """Search for records based on approval.log user_id"""
        model_id = self.env["ir.model"]._get_id(self._name)
        if operator == "=":
            # Find all approval.log records with matching user_id
            log_records = self.env["approval.log"].search_fetch(
                [("model_id", "=", model_id), ("user_id", "=", value)],
                ["record_id"],
            )
            # Get unique record_ids from the logs
            record_ids = log_records.mapped("record_id")
            if not record_ids:
                return [(0, "=", 1)]  # Return empty domain if no matches
            return [("id", "in", record_ids)]
        elif operator == "!=":
            # Find all approval.log records with non-matching user_id
            log_records = self.env["approval.log"].search_fetch(
                [("model_id", "=", model_id), ("user_id", "!=", value)],
                ["record_id"],
            )
            record_ids = log_records.mapped("record_id")
            if not record_ids:
                return [(0, "=", 1)]  # Return empty domain if no matches
            return [("id", "in", record_ids)]
        elif operator == "in":
            # Find all approval.log records with user_id in the list
            log_records = self.env["approval.log"].search_fetch(
                [("model_id", "=", model_id), ("user_id", "in", value)],
                ["record_id"],
            )
            record_ids = log_records.mapped("record_id")
            if not record_ids:
                return [(0, "=", 1)]  # Return empty domain if no matches
            return [("id", "in", record_ids)]
        else:
            # For other operators, return empty domain (could be extended)
            return [(0, "=", 1)]

    @api.depends("state", "status_id", "user_can_approve")
    def _calc_button_enabled(self):
        for record in self:
            need_approval = bool(
                record.status_id or record.state in self._before_approval_states_values()
            )
            user_can_approve = (
                record.state in self._before_approval_states_values()
                or record.user_can_approve
            )
            record.button_approve_enabled = need_approval and user_can_approve
            record.button_forward_enabled = (
                record.user_can_approve and record.status_id.allow_forward
            )
            record.button_return_enabled = (
                record.user_can_approve and record.status_id.allow_return
            )
            record.button_transfer_enabled = (
                record.user_can_approve and record.status_id.allow_transfer
            )
            record.button_cancel_enabled = (
                record.user_can_approve and record.status_id.allow_cancel
            )

    @api.depends("state")
    def _calc_button_confirm_enabled(self):
        for record in self:
            record.button_confirm_enabled = record.state == record._get_draft_state()

    @api.depends("state")
    def _calc_button_draft_enabled(self):
        for record in self:
            record.button_draft_enabled = record.state != record._get_draft_state()

    def _on_approve(self):
        "on user approve, approve state"
        self.state = self._get_approved_state()

    def _on_script_custom(self, name, **kwargs):
        script = self.env["approval.settings"].get(self._name)[name]
        if script:
            eval_context = self._get_eval_context()
            eval_context.update(kwargs)
            safe_eval(script, eval_context, mode="exec", nocopy=True)
            return eval_context.get("action") or True
        return False

    def _on_submit(self):
        "on user submit, first approval state"
        pass

    def _on_approval(self, old_state, new_state):
        "on user approve, next state"
        pass

    def _on_reject(self):
        "on user reject"
        pass

    def _on_cancel(self):
        "on user reject"
        pass

    def _get_activity_record(self):
        return self

    def _schedule_approval_activity(self, users=None):
        if users is None:
            users = self.approval_user2_ids

        if "workflow_advanced" in self and self.workflow_advanced:
            status_id = self.workflow_node_id
        else:
            status_id = self.status_id
        if not status_id.schedule_activity:
            return
        if status_id.schedule_activity_field_id:
            date_deadline = self[
                status_id.schedule_activity_field_id.name
            ] or fields.Date.context_today(self)
        else:
            date_deadline = fields.Date.context_today(self)
            date_deadline += timedelta(days=status_id.schedule_activity_days)

        activity_record = self._get_activity_record()

        for user in users:
            self.env["mail.activity"].sudo().with_context(
                disable_message_subscribe=True, mail_activity_quick_update=True
            ).create(
                {
                    "user_id": user.id,
                    "res_id": activity_record.id,
                    "res_model_id": self.env["ir.model"]._get_id(activity_record._name),
                    "activity_type_id": self.env.ref(
                        "eds_workflow.activity_type_approval"
                    ).id,
                    "summary": _("Waiting Approval"),
                    "date_deadline": date_deadline,
                    "automated": True,
                }
            )

    def _remove_approval_activity(
        self,
        action=None,
        reason=None,
        old_state_id=None,
        user_id=None,
        forward_user=None,
    ):
        model_id = self.env["ir.model"]._get_id(self._name)
        self.env["approval.forward"].sudo().search_fetch(
            [
                ("model_id", "=", model_id),
                ("record_id", "in", self.ids),
                ("active", "=", True),
            ],
            ["id"],
        ).write({"active": False})
        for record in self:
            activity_record = record._get_activity_record()

            domain = [
                ("res_model", "=", activity_record._name),
                ("res_id", "=", activity_record.id),
                (
                    "activity_type_id",
                    "=",
                    self.env.ref("eds_workflow.activity_type_approval").id,
                ),
            ]
            if user_id:
                domain.append(("user_id", "=", user_id))
            activity_ids = self.env["mail.activity"].sudo().search_fetch(domain, ["id"])
            activity_ids.unlink()
            post_msg = (
                (action == "approved" and old_state_id.post_approval_msg)
                or (action == "rejected" and old_state_id.post_reject_msg)
                or action == "return"
                or action == "forward"
                or action == "transfer"
                or action == "cancelled"
            )
            if action and activity_record._isinstance("mail.thread") and post_msg:
                view_xmlid = "eds_workflow.approval_record_%s" % action
                values = {
                    "record": activity_record,
                    "user": self.env.user,
                    "reason": reason,
                    "forward_user": forward_user,
                }
                activity_record.message_post_with_source(
                    view_xmlid,
                    render_values=values,
                    subtype_id=self.env.ref("mail.mt_activities").id,
                    mail_activity_type_id=self.env.ref(
                        "eds_workflow.activity_type_approval"
                    ).id,
                )

    def _update_approval_activity(self):
        activity_record = self._get_activity_record()
        domain = [
            ("res_model", "=", activity_record._name),
            ("res_id", "=", activity_record.id),
            (
                "activity_type_id",
                "=",
                self.env.ref("eds_workflow.activity_type_approval").id,
            ),
        ]
        activity_ids = self.env["mail.activity"].search_fetch(domain, ["user_id"])
        activity_to_delete = self.env["mail.activity"]

        for activity_id in activity_ids:
            if (
                activity_id.user_id not in self.approval_user2_ids
                or not self.status_id.schedule_activity
            ):
                activity_to_delete += activity_id

        self._schedule_approval_activity(
            users=self.approval_user2_ids - activity_ids.mapped("user_id")
        )
        activity_to_delete.unlink()

    def action_approve(self):
        self = self.filtered("button_approve_enabled")

        actions = []

        def append_actions(action):
            if isinstance(action, list):
                actions.extend(action)
            elif action:
                actions.append(action)

        for record in self:
            if record.status_id.is_sudo_approve:
                record = self.sudo()

            append_actions(record._action_approve())

            if record.status_id.auto_approve and record.button_approve_enabled:
                append_actions(record.action_approve())

        return self._clean_actions(actions)

    @api.model
    def _clean_actions(self, actions):
        actions = list(filter(lambda a: a and isinstance(a, dict), actions))
        if actions:
            if len(actions) > 1 and "ir.actions.act_multi" in self.env:
                return {"type": "ir.actions.act_multi", "actions": actions}
            return actions[0]

    def _send_approval_survey(self, old_state, new_state):
        pass

    def _action_approve(self):

        actions = []
        for record in self:
            old_state = record.state
            old_state_id = record.status_id
            if not old_state_id:
                actions.append(
                    record._on_script_custom("on_submit") or record._on_submit()
                )
                if record.stop_approval_trigger:
                    continue

            nextstate = record.status_id._get_next(record)
            if old_state_id.on_script:
                actions.append(
                    safe_eval(
                        old_state_id.on_script, record._get_eval_context(), mode="exec"
                    )
                )
            if not nextstate:
                actions.append(
                    record._on_script_custom(
                        "on_approval", old_state=old_state, new_state=record.state
                    )
                    or record._on_approval(old_state, record.state)
                )
                if record.stop_approval_trigger:
                    continue

                actions.append(
                    record._on_script_custom("on_approve") or record._on_approve()
                )
                if record.stop_approval_trigger:
                    continue
                record._send_approval_survey(
                    old_state=old_state, new_state=record.state
                )
            else:
                if record.state != nextstate.state:
                    record.state = nextstate.state
                    record._send_approval_survey(
                        old_state=old_state, new_state=record.state
                    )
                    actions.append(
                        record._on_script_custom(
                            "on_approval", old_state=old_state, new_state=record.state
                        )
                        or record._on_approval(old_state, record.state)
                    )
                    if record.stop_approval_trigger:
                        continue

            if old_state != record.state:
                record._remove_approval_activity("approved", old_state_id=old_state_id)
                if not self._context.get("approval_no_mail"):
                    for template_id in nextstate.template_ids:
                        template_id.with_context(active_model=self._name).send_mail(
                            record.id
                        )
                    if nextstate.auto_subscribe_users:
                        record.message_subscribe(
                            partner_ids=record.approval_user2_ids.mapped(
                                "partner_id.id"
                            )
                        )
                    if nextstate.schedule_activity:
                        record._schedule_approval_activity()
                if nextstate.before_script:
                    actions.append(
                        safe_eval(
                            nextstate.before_script,
                            record._get_eval_context(),
                            mode="exec",
                        )
                    )
                if old_state_id.after_script:
                    actions.append(
                        safe_eval(
                            old_state_id.after_script,
                            record._get_eval_context(),
                            mode="exec",
                        )
                    )

        return self._clean_actions(actions)

    def action_reject(self, reason=None):
        self = self.filtered("button_approve_enabled")
        return self._action_reject(reason=reason)

    def _action_reject(self, reason=None):
        self = self.filtered("button_approve_enabled")

        actions = []

        for record in self:
            record._remove_approval_activity(
                "rejected", reason, old_state_id=record.status_id
            )
            reject_script = record.status_id.reject_script
            state = ""
            old_state = record.state
            if reject_script:
                localdict = record._get_eval_context()
                localdict["reason"] = reason
                safe_eval(reject_script, localdict, mode="exec", nocopy=True)
                state = localdict.get("state")
            reject_template_ids = record.status_id.reject_template_ids
            record.with_context(reject_reason=reason).write(
                {"state": state or self._get_reject_state()}
            )
            for template in reject_template_ids:
                template.with_context(
                    active_model=self._name, reject_reason=reason
                ).send_mail(record.id)
            actions.append(
                record._on_script_custom("on_reject", old_state=old_state)
                or record._on_reject()
            )

        return self._clean_actions(actions)

    def action_reject_wizard(self):
        context = dict(self._context)
        context.update(
            {"active_model": self._name, "active_ids": self.ids, "active_id": self.id}
        )
        model_id = self.env["ir.model"]._get(self._name)
        return {
            "type": "ir.actions.act_window",
            "name": _("Reject %s : %s") % (model_id.name, self.display_name),
            "res_model": "approval.reject.wizard",
            "target": "new",
            "view_mode": "form",
            "view_type": "form",
            "context": context,
        }

    def action_approve_wizard(self):
        context = dict(self._context)
        context.update(
            {"active_model": self._name, "active_ids": self.ids, "active_id": self.id}
        )
        model_id = self.env["ir.model"]._get(self._name)
        return {
            "type": "ir.actions.act_window",
            "name": _("Approve %s : %s") % (model_id.name, self.display_name),
            "res_model": "approval.approve.wizard",
            "target": "new",
            "view_mode": "form",
            "view_type": "form",
            "context": context,
        }

    def action_request_draft(self):
        records = self.filtered("button_draft_enabled")
        self._remove_approval_activity()
        records.write({"state": self._get_draft_state()})

    @api.model_create_multi
    def create(self, vals_list):
        now = fields.Datetime.now()
        for vals in vals_list:
            vals.setdefault("last_state_update", now)
        records = super(ApprovalRecord, self).create(vals_list)
        for record in records:
            record._after_save()
        return records

    def write(self, vals):
        reject_reason = self._context.get("reject_reason")
        if "state" in vals:
            vals["last_state_update"] = fields.Datetime.now()
        states = self._read_field("state")
        res = super(ApprovalRecord, self).write(vals)
        self._after_save(vals, states, reject_reason)
        return res

    def _after_save(self, vals=None, old_states={}, reject_reason=False):
        if vals is None or "state" in vals:
            model_id = self.env["ir.model"]._get_id(self._name)
            for record in self:
                if record.state != old_states.get(record.id) and old_states.get(
                    record.id
                ):
                    self.env["approval.log"].sudo().create(
                        {
                            "record_id": record.id,
                            "user_id": self.env.user.id,
                            "date": fields.Datetime.now(),
                            "state": record.state,
                            "model_id": model_id,
                            "description": reject_reason,
                        }
                    )

    def unlink(self):
        for record in self:
            if record.state != self._get_draft_state():
                raise ValidationError(
                    _("You can delete in %s status only") % self._get_draft_state()
                )
        model_id = self.env["ir.model"]._get_id(self._name)
        self.env["approval.log"].sudo().search_fetch(
            [("model_id", "=", model_id), ("record_id", "in", self.ids)],
            ["id"],
        ).unlink()
        return super(ApprovalRecord, self).unlink()

    @api.model
    def _create_approval_settings(self):
        model_id = self.env["ir.model"]._get_id(self._name)
        record = self.env["approval.settings"].search_fetch(
            [("model_id", "=", model_id)], ["model_id"]
        )
        if model_id and not record:
            record = self.env["approval.settings"].create({"model_id": model_id})
        if record:
            record.with_context(is_approval_setting=True)._create_external_id()

    def init(self):
        super(ApprovalRecord, self).init()
        if not self._abstract:
            self.pool.post_init(self._create_approval_settings)

    def action_forward(self):
        context = dict(self._context)
        context.update(
            {"active_model": self._name, "active_ids": self.ids, "active_id": self.id}
        )
        model_id = self.env["ir.model"]._get(self._name)
        return {
            "type": "ir.actions.act_window",
            "name": _("Forward %s : %s") % (model_id.name, self.display_name),
            "res_model": "approval.forward.wizard",
            "target": "new",
            "view_mode": "form",
            "view_type": "form",
            "context": context,
        }

    def action_return(self):
        context = dict(self._context)
        context.update(
            {"active_model": self._name, "active_ids": self.ids, "active_id": self.id}
        )
        if self._context.get("fixed_return_state"):
            context.update({"default_state": self._context.get("fixed_return_state")})
        model_id = self.env["ir.model"]._get(self._name)
        return {
            "type": "ir.actions.act_window",
            "name": _("Return %s : %s") % (model_id.name, self.display_name),
            "res_model": "approval.return.wizard",
            "target": "new",
            "view_mode": "form",
            "view_type": "form",
            "context": context,
        }

    def action_transfer(self):
        context = dict(self._context)
        context.update(
            {"active_model": self._name, "active_ids": self.ids, "active_id": self.id}
        )
        if self._context.get("fixed_transfer_state"):
            context.update({"default_state": self._context.get("fixed_transfer_state")})
        model_id = self.env["ir.model"]._get(self._name)
        return {
            "type": "ir.actions.act_window",
            "name": _("Transfer %s : %s") % (model_id.name, self.display_name),
            "res_model": "approval.transfer.wizard",
            "target": "new",
            "view_mode": "form",
            "view_type": "form",
            "context": context,
        }

    def action_cancel(self):
        if not self.status_id and hasattr(self, "action_cancel"):
            return super(ApprovalRecord, self).action_cancel()
        context = dict(self._context)
        context.update(
            {"active_model": self._name, "active_ids": self.ids, "active_id": self.id}
        )
        model_id = self.env["ir.model"]._get(self._name)
        return {
            "type": "ir.actions.act_window",
            "name": _("Cancel %s : %s") % (model_id.name, self.display_name),
            "res_model": "approval.cancel.wizard",
            "target": "new",
            "view_mode": "form",
            "view_type": "form",
            "context": context,
        }

    def _action_forward(self, user_id, reason):
        self = self.filtered("button_approve_enabled")
        model_id = self.env["ir.model"]._get_id(self._name)

        for record in self:
            record._remove_approval_activity(
                action="forward", reason=reason, forward_user=user_id
            )
            self.env["approval.forward"].sudo().create(
                {
                    "model_id": model_id,
                    "record_id": record.id,
                    "status_id": record.status_id.id,
                    "user_id": user_id.id,
                    "forwarder_user_id": self.env.user.id,
                    "reason": reason,
                }
            )

        # self.env.cache.invalidate()

        actions = []
        for record in self:
            record._schedule_approval_activity()
            actions.append(
                record._on_script_custom("on_forward", user_id=user_id, reason=reason)
                or record._on_forward(user_id=user_id, reason=reason)
            )

            if not self._context.get("approval_no_mail"):
                for template_id in record.status_id.template_ids:
                    template_id.with_context(
                        active_model=self._name,
                        reason=reason,
                        forwarder_user=self.env.user,
                    ).send_mail(record.id)

        return self._clean_actions(actions)

    def _action_return(self, state, reason):
        self = self.filtered("button_approve_enabled")
        old_states = {}
        for record in self:
            old_states[record] = record.state
            record._remove_approval_activity(action="return", reason=reason)
            record.with_context(reject_reason=reason).write({"state": state})

        # self.env.cache.invalidate()

        actions = []
        for record in self:
            record._schedule_approval_activity()
            actions.append(
                record._on_script_custom(
                    "on_return",
                    new_state=state,
                    old_state=old_states[record],
                    reason=reason,
                )
                or record._on_return(
                    new_state=state, old_state=old_states[record], reason=reason
                )
            )

        return self._clean_actions(actions)

    def _action_transfer(self, state, reason):
        self = self.filtered("button_approve_enabled")
        old_states = {}
        for record in self:
            old_states[record] = record.state
            record._remove_approval_activity(action="transfer", reason=reason)
            record.with_context(reject_reason=reason).write({"state": state})

        # self.env.cache.invalidate()

        actions = []
        for record in self:
            record._schedule_approval_activity()
            actions.append(
                record._on_script_custom(
                    "on_transfer",
                    new_state=state,
                    old_state=old_states[record],
                    reason=reason,
                )
                or record._on_transfer(
                    new_state=state, old_state=old_states[record], reason=reason
                )
            )

        return self._clean_actions(actions)

    def _on_forward(self, user_id=None, reason=None):
        pass

    def _on_return(self, new_state=None, old_state=None, reason=None):
        pass

    def _on_transfer(self, new_state=None, old_state=None, reason=None):
        pass

    def _expand_states(self, states, domain, order):
        values = self._fields["state"].get_values(self.env)
        if self._context.get("expand_states_full"):
            return values
        return sorted(
            states, key=lambda state: values.index(state) if state in values else 9999
        )

    def get_approval_info(self):
        self.ensure_one()

        if self._name == "stock.picking":
            self = self.approval_id

        data = {
            "lines": [],
            "show_login_as": bool(
                self.env.user._is_system()
                and self.env["ir.module.module"]._installed().get("eds_login_as")
            ),
        }

        self.check_access_rights("read")
        self.check_access_rule("read")

        self = self.sudo()

        if self._isinstance("approval.record"):
            data["name"] = self.display_name
            approval_user2_ids = self.mapped("approval_user2_ids")
            if "committee" in self.status_id and self.status_id.committee:

                def is_approved(user):
                    for log_id in self.log_ids:
                        if log_id.state != self.state:
                            break
                        if log_id.user_id == user:
                            return True
                    return False

                for user in list(approval_user2_ids):
                    if is_approved(user):
                        approval_user2_ids -= user

            data["approval_users"] = []
            for user in approval_user2_ids:
                data["approval_users"].append((user.id, user.get_display_name()))
            data["waiting_approval"] = self.waiting_approval

            for log in self.log_ids:
                data["lines"].append(
                    {
                        "user": log.user_id.get_display_name(),
                        "date": format_datetime(self.env, log.date, dt_format=False),
                        "old": log.old_name or "",
                        "new": log.name,
                        "description": log.description or "",
                        "duration": "duration" in log and log.duration or None,
                    }
                )
            data["workflow"] = (
                self.workflow_id.name if hasattr(self, "workflow_id") else ""
            )
            data["workflow_node"] = (
                self.workflow_node_id.name if hasattr(self, "workflow_node_id") else ""
            )
            data["workflow_activity"] = (
                self.workflow_activity_ids.mapped("name")
                if hasattr(self, "workflow_activity_ids")
                else []
            )

        return data

    def action_approve_all(self):
        self.action_approve()
        return {"type": "ir.actions.client", "tag": "soft_reload"}

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "tree":
            for node in arch.xpath("//tree"):
                if (
                    self.env["approval.settings"]
                    .get(self._name)
                    .show_action_approve_all
                ):
                    node.set("show_action_approve_all", "true")

        return arch, view
