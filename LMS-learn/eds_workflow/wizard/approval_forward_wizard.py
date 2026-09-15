"""
Created on Nov 11, 2019

@author: Zuhair Hammadi
"""

from odoo import api, fields, models
from odoo.exceptions import AccessError


class ApprovalForwardWizard(models.TransientModel):
    _name = "approval.forward.wizard"
    _description = "Approval Forward Wizard"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        self._get_user_id_domain()
        return res

    @api.model
    def _get_user_id_domain(self):
        if not self._context.get("active_model"):
            return []

        if self._context.get("forward_no_domain"):
            return []

        model_id = self.env["ir.model"]._get(self._context.get("active_model"))
        record = self.env[model_id.model].browse(self._context.get("active_id"))

        if self._context.get("forward_to_group"):
            users_ids = []
            groups = self.env["res.groups"]
            for g in self._context.get("forward_to_group").split(","):
                groups += self.env.ref(g, False) or self.env["res.groups"]

            for group in groups:
                for user in group.users:
                    users_ids.append(user.id)
            self.user_ids = users_ids
            return [("id", "in", users_ids)]

        users = (
            model_id.access_ids.filtered("perm_write").mapped("group_id.users")
            - record.approval_user_ids
        )

        if self._context.get("forward_ignore_access_rule"):
            self.user_ids = users.ids
            return [("id", "in", users.ids)]

        ids = []
        for user in users:
            try:
                record = record.sudo(user.id)
                record.check_access_rule("read")
                record.check_access_rule("write")
                ids.append(user.id)
            except AccessError:
                pass
        self.user_ids = ids
        return [("id", "in", ids)]

    model = fields.Char(
        default=lambda self: self._context.get("active_model"), required=True
    )
    record_id = fields.Integer(
        default=lambda self: self._context.get("active_id"),
        required=True,
        string="Record ID",
    )
    record_ref = fields.Char("Record", compute="_calc_record_ref")

    reason = fields.Text(required=True)
    user_id = fields.Many2one("res.users", required=True)
    user_ids = fields.Many2many("res.users", compute="_get_users")

    @api.depends("model", "record_id")
    def _get_users(self):
        if not self._context.get("active_model"):
            return []

        if self._context.get("forward_no_domain"):
            return []

        model_id = self.env["ir.model"]._get(self._context.get("active_model"))
        record = self.env[model_id.model].browse(self._context.get("active_id"))

        if self._context.get("forward_to_group"):
            users_ids = []
            groups = self.env["res.groups"]
            for g in self._context.get("forward_to_group").split(","):
                groups += self.env.ref(g, False) or self.env["res.groups"]

            for group in groups:
                for user in group.users:
                    users_ids.append(user.id)
            self.user_ids = users_ids
            return [("id", "in", users_ids)]

        users = (
            model_id.access_ids.filtered("perm_write").mapped("group_id.users")
            - record.approval_user_ids
        )

        if self._context.get("forward_ignore_access_rule"):
            self.user_ids = users.ids
            return [("id", "in", users.ids)]

        ids = []
        for user in users:
            try:
                record = record.sudo(user.id)
                record.check_access_rule("read")
                record.check_access_rule("write")
                ids.append(user.id)
            except AccessError:
                pass
        self.user_ids = ids
        return [("id", "in", ids)]

    @api.depends("model", "record_id")
    def _calc_record_ref(self):
        for wizard in self:
            record = self.env[wizard.model].browse(wizard.record_id).exists()
            wizard.record_ref = record and "%s,%d" % (record._name, record.id)

    def action_forward(self):
        record = self.env[self.model].browse(self.record_id)
        action = record._action_forward(self.user_id, self.reason)
        return action or {"type": "ir.actions.client", "tag": "soft_reload"}
