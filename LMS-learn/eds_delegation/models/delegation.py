"""
Created on Dec 19, 2016

@author: zuhair
"""

from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

Overlap_SQL = """
select delegation.id
from delegation
    inner join delegation_line on delegation_line.delegation_id = delegation.id
where delegation.employee_id = %(employee_id)d
and delegation.state = 'confirmed'
and delegation_line.group_id = %(group_id)d
and delegation_line.active
and '%(date_from)s' <= delegation.date_to
and '%(date_to)s' >= delegation.date_from
limit 1
"""


class Delegation(models.Model):
    _name = "delegation"
    _description = "Delegation"
    _order = "id desc"

    @api.model
    def _get_lines(self):
        lines = []
        groups = []
        for group in self.env.user.group_ids:
            if group.allow_delegation:
                groups.append((group.display_name, group))
        for _, group in sorted(groups):
            lines.append((0, 0, {"group_id": group.id}))
        return lines

    name = fields.Char("Request Number", required=True, default="New", readonly=True)
    date_from = fields.Date("From Date", required=True)
    date_to = fields.Date("To Date", required=True)

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        ondelete="restrict",
        required=True,
        default=lambda self: self.env.user.employee_id,
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        related="employee_id.user_id",
        readonly=True,
        store=True,
        default=lambda self: self.env.user,
    )

    one_employee = fields.Boolean("All Roles to one employee")
    stop_receiving_notification = fields.Boolean("Stop Receiving Notifications")
    delegateTo_employee_ids = fields.Many2many(
        "hr.employee", compute="_compute_delegate_domain", string="Employees"
    )

    delegateTo_employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        ondelete="restrict",
        # domain=lambda self: self._get_delegate_domain(),
    )

    is_delegation_admin = fields.Boolean(
        string="Is Delegation Admin",
        compute="_compute_is_delegation_admin",
    )

    @api.depends("employee_id")
    def _compute_is_delegation_admin(self):
        for record in self:
            if not self.env.user.has_group("eds_delegation.delegation_admin"):
                record.is_delegation_admin = False
            else:
                record.is_delegation_admin = True

    @api.depends("employee_id")
    def _compute_delegate_domain(self):
        employee_obj = self.env["hr.employee"]
        for rec in self:
            domain = [
                ("id", "!=", rec.employee_id.id),
                "|",
                ("parent_id", "=", rec.employee_id.id),
                ("parent_id.child_ids", "=", rec.employee_id.id),
            ]
            if not self.env.user.has_group("eds_delegation.delegation_admin"):
                domain.append(("company_id", "=", self.env.company.id))
            employee_domain = employee_obj.search(domain)
            rec.delegateTo_employee_ids = employee_domain

    def _get_delegate_domain(self):

        domain = [
            ("id", "!=", self.employee_id.id),
            "|",
            ("parent_id", "=", self.employee_id.id),
            ("parent_id.child_ids", "=", self.employee_id.id),
        ]
        if not self.env.user.has_group("eds_delegation.delegation_admin"):
            domain.append(("company_id", "=", self.env.company.id))
        return domain

    empty = fields.Boolean(compute="_calc_empty")

    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("revoked", "Revoked")],
        default="draft",
        string="Status",
        copy=False,
        required=True,
    )

    isactive = fields.Boolean(string="Active", compute="_calc_active")

    lines = fields.One2many("delegation.line", "delegation_id")

    @api.constrains("user_id")
    def _constrains_user_id(self):
        for rec in self:
            if not rec.user_id:
                raise ValidationError(_("Employee should linked with user"))

    _sql_constraints = [("name_uk", "unique(name)", "Request Number should be unique")]

    def init(self):
        self._cr.execute(
            "CREATE INDEX IF NOT EXISTS delegation_write_date_ix on delegation(write_date NULLS LAST) where state!='draft'"
        )
        self._cr.execute(
            "CREATE INDEX IF NOT EXISTS res_users_write_date_ix on res_users(write_date NULLS LAST)"
        )
        super(Delegation, self).init()

    @api.depends("state", "date_from", "date_to")
    def _calc_active(self):
        today = fields.Date.today()
        for record in self:
            record.isactive = (
                record.state == "confirmed"
                and today >= record.date_from
                and today <= record.date_to
            )

    @api.depends("lines")
    def _calc_empty(self):
        for record in self:
            record.empty = not any(record.mapped("lines.employee_id"))

    def action_confirm(self):
        if not self:
            return
        if self.empty:
            raise ValidationError(_("No roles assigned"))
        if self.date_from < fields.Date.today():
            raise ValidationError(_("You cannot submit a delegation with old date"))
        cr = self._cr
        for line in self.lines.filtered(
            lambda line: line.employee_id
            and not line.group_id.allow_multiple_delegation
        ):
            sql = Overlap_SQL % {
                "employee_id": self.employee_id.id,
                "group_id": line.group_id.id,
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
            cr.execute(sql)
            res = cr.fetchone()
            if res:
                raise ValidationError(
                    _("You cannot submit overlapped delegation for %s")
                    % (line.group_id.display_name,)
                )
        self.state = "confirmed"
        template_id = self.env.ref("eds_delegation.email_template_delegation", False)
        if template_id:
            delegators = {}
            for line in self.lines.filtered("employee_id"):
                delegators.setdefault(line.employee_id.id, []).append(
                    line.group_id.display_name
                )

            for employee_id, roles in delegators.items():
                employee = self.env["hr.employee"].browse(employee_id)
                context = dict(self._context)
                context["roles"] = ", ".join(roles)
                context["delegator"] = employee.name
                context["delegator_email"] = employee.work_email
                context["delegator_mngr_email"] = employee.parent_id.work_email
                template_id.with_context(context).send_mail(self.id)

    def action_revoked(self):
        self.ensure_one()
        if self.date_to < fields.Date.today():
            raise ValidationError(_("You cannot revoke a delegation with old date"))
        self.state = "revoked"

    @api.constrains("date_from", "date_to")
    def _check_date(self):
        for record in self:
            if record.date_from > record.date_to:
                raise ValidationError(_("From Date > To Date"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("delegation")
        return super(Delegation, self).create(vals_list)

    def write(self, vals):
        res = super(Delegation, self).write(vals)
        if "state" in vals:
            self._clear_access_cache()
        return res

    @api.model
    def _clear_access_cache(self):
        for model in ["ir.model.access", "res.users", "ir.rule", "ir.ui.menu"]:
            self.env[model].invalidate_model()
        self.env["ir.model.access"].call_cache_clearing_methods()
        # Clear ormcache for load_menus/load_web_menus so delegation changes
        # are reflected immediately in the menu service
        self.env.registry.clear_cache()

    def unlink(self):
        for record in self:
            if record.state != "draft":
                raise ValidationError(_("Only draft can be deleted"))
        return super(Delegation, self).unlink()

    def action_submit(self):
        pass

    @api.onchange("user_id")
    def _onchange_user_id(self):
        if self.user_id:
            self.lines = False
            group_ids = self.user_id.group_ids.filtered("allow_delegation").sorted(
                "display_name"
            )
            for group_id in group_ids:
                self.lines += self.env["delegation.line"].new({"group_id": group_id.id})

    @api.onchange("delegateTo_employee_id")
    def _on_change_employee_id(self):
        self.lines.write({"employee_id": self.delegateTo_employee_id.id})

    @api.onchange("one_employee")
    def _on_change_one_employee(self):
        if not self.one_employee:
            self.delegateTo_employee_id = False

    @api.constrains("employee_id", "delegateTo_employee_id")
    def _check_delegateTo_employee_id(self):
        for record in self:
            if record.delegateTo_employee_id == record.employee_id:
                raise ValidationError(
                    _("the delegator should not been able to delegate himself")
                )
