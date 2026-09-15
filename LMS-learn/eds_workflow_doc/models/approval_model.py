"""
Created on Mar 27, 2019

@author: Zuhair Hammadi
"""

import json
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

_form_arch = """
<data>
  <sheet>
    <group>
%(groups)s
    </group>
    <notebook>
%(pages)s    
    </notebook>
  </sheet>
</data>        
"""

_tree_arch = """

<list>
%s
</list>
"""

_search_arch = """
<data>
  <search>
%s
  </search>
</data>
"""


class ApprovalModel(models.Model):
    _name = "approval.model"
    _description = _name
    _inherits = {'ir.model': 'model_id'}

    model_id = fields.Many2one(
        "ir.model",
        string="Object",
        required=True,
        delegate=True,
        readonly=True,
        ondelete="cascade",
    )

    sequence_id = fields.Many2one("ir.sequence", readonly=True)

    form_view_id = fields.Many2one("ir.ui.view", readonly=True)
    tree_view_id = fields.Many2one("ir.ui.view", readonly=True)
    search_view_id = fields.Many2one("ir.ui.view", readonly=True)

    field_ids = fields.Many2many(
        "ir.model.fields", compute="_calc_field_ids", inverse="_set_field_ids"
    )

    approval_count = fields.Integer(compute="_calc_approval_count")
    records_count = fields.Integer(compute="_calc_records_count")
    details_model_count = fields.Integer(compute="_calc_details_model_count")
    views_count = fields.Integer(compute="_calc_views_count")
    action_count = fields.Integer(compute="_calc_action_count")
    cron_count = fields.Integer(compute="_calc_cron_count")
    fields_count = fields.Integer(compute="_calc_fields_count")
    excel_count = fields.Integer(compute="_calc_excel_count")

    display_ids = fields.One2many("approval.model.display", "approval_model_id")
    page_ids = fields.One2many("approval.model.page", "approval_model_id")
    tree_ids = fields.One2many("approval.model.tree", "approval_model_id")

    details_model_ids = fields.One2many("ir.model", "parent_approval_model_id")

    menu_id = fields.Many2one("ir.ui.menu", readonly=True)

    category_id = fields.Many2one("approval.model.category", required=True)

    kanban_dashboard = fields.Text(compute="_calc_kanban_dashboard")
    color = fields.Integer("Color Index", default=0)
    description = fields.Text()

    restrict_department_ids = fields.Many2many(
        "hr.department", string="Allowed Departments"
    )
    restrict_group_ids = fields.Many2many("res.groups", string="Allowed Groups")

    show_on_dashboard = fields.Boolean(
        string="Show on Model dashboard",
        help="Whether this Model should be displayed on the dashboard or not",
        default=True,
    )
    active = fields.Boolean(default=True)

    name = fields.Char(related="model_id.name", compute_sudo=True, readonly=False)

    model = fields.Char(related="model_id.model", compute_sudo=True, readonly=False)

    @api.onchange("name")
    def _onchange_name(self):
        if self.name and self.model == "x_":
            self.model = "x_%s" % re.sub(
                r"[\W_]", " ", self.name.lower()
            ).strip().replace(" ", "_")

    @api.depends("model_id")
    def _calc_kanban_dashboard(self):

        for record in self:
            record.kanban_dashboard = json.dumps(record.get_kanban_dashboard())

    @api.depends("model_id")
    def _calc_views_count(self):
        for record in self:
            record.views_count = self.env["ir.ui.view"].search_count(
                [("model", "=", record.model_id.model)]
            )

    @api.depends("model_id")
    def _calc_action_count(self):
        for record in self:
            record.action_count = self.env["ir.actions.server"].search_count(
                [
                    ("model_id", "=", record.model_id.id),
                    ("usage", "=", "ir_actions_server"),
                ]
            )

    @api.depends("model_id")
    def _calc_cron_count(self):
        for record in self:
            record.cron_count = self.env["ir.cron"].search_count(
                [("model_id", "=", record.model_id.id)]
            )

    @api.depends("model_id")
    def _calc_fields_count(self):
        for record in self:
            record.fields_count = self.env["ir.model.fields"].search_count(
                [("model_id", "=", record.model_id.id)]
            )

    @api.depends("field_id")
    def _calc_field_ids(self):
        for record in self:
            record.field_ids = record.field_id.filtered(lambda f: f.state == "manual")

    def _set_field_ids(self):
        for field_id in self.field_id.filtered(lambda f: f.state == "manual"):
            if field_id not in self.field_ids:
                field_id.unlink()

        for field_id in self.field_ids:
            if isinstance(field_id.id, models.NewId):
                vals = {
                    fname: field_id[fname]
                    for fname, field in field_id._fields.items()
                    if field.store and not field.automatic
                }
                vals = field_id._convert_to_write(vals)
                vals["state"] = "manual"
                vals["model_id"] = self.model_id.id
                if vals.get("name"):
                    field_id.create(vals)

    @api.depends("model_id")
    def _calc_approval_count(self):
        for record in self:
            record.approval_count = self.env["approval.config"].search_count(
                [("model_id", "=", record.model_id.id)]
            )

    @api.depends("model_id")
    def _calc_records_count(self):
        for record in self:
            if record.model_id.model in self.env:
                cr = self._cr
                cr.execute(
                    "select count(*) from %s" % self.env[record.model_id.model]._table
                )
                (record.records_count,) = cr.fetchone()
            else:
                record.records_count = 0

    @api.depends("model_id")
    def _calc_excel_count(self):
        for record in self:
            record.excel_count = self.env["approval.model.excel"].search_count(
                [("approval_model_id", "=", record.id)]
            )

    @api.depends("details_model_ids")
    def _calc_details_model_count(self):
        for record in self:
            record.details_model_count = len(record.details_model_ids)

    def get_kanban_dashboard(self):
        model = self.env[self.model]
        res = {"states": [], "title": self.description or ""}
        if not model.check_access_rights("read", False):
            return res

        states = model.read_group([], ["state"], ["state"])
        selection = model._fields["state"]._description_selection(self.env)

        def state_index(state):
            index = 0
            for s in selection:
                if s[0] == state:
                    break
                index += 1
            else:
                index = 9999
            return index

        state_names = dict(selection)
        for vals in states:
            vals["name"] = state_names.get(vals["state"], vals["state"])
            vals["seq"] = state_index(vals["state"])

        res["states"] = sorted(states, key=lambda item: item["seq"])

        return res

    def action_view_approval(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Workflow",
            "res_model": "approval.settings",
            "view_mode": "form",
            "res_id": self.env["approval.settings"]
            .search([("model_id", "=", self.model_id.id)])
            .id,
        }

    def action_view_views(self):
        model = self.model_id.model
        return {
            "type": "ir.actions.act_window",
            "name": "Views",
            "res_model": "ir.ui.view",
            "view_mode": ",form",
            "context": {"default_model": model},
            "domain": [("model", "=", model)],
        }

    def action_view_action(self):
        model_id = self.model_id.id
        (action,) = self.env.ref("base.action_server_action").read([])
        action["domain"] = [("model_id", "=", model_id)]
        action["context"] = safe_eval(action.get("context") or "{}")
        action["context"].update({"default_model_id": model_id})
        return action

    def action_view_cron(self):
        model_id = self.model_id.id
        (action,) = self.env.ref("base.ir_cron_act").read([])
        action["domain"] = [("model_id", "=", model_id)]
        action["context"] = safe_eval(action.get("context") or "{}")
        action["context"].update({"default_model_id": model_id})
        return action

    def action_view_fields(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Fields",
            "res_model": "ir.model.fields",
            "view_mode": ",form",
            "context": {
                "default_model_id": self.model_id.id,
                "search_default_custom": 1,
            },
            "domain": [("model_id", "=", self.model_id.id)],
        }

    def action_view_excel(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Excel Report",
            "res_model": "approval.model.excel",
            "view_mode": ",form",
            "context": {"default_approval_model_id": self.id},
            "domain": [("approval_model_id", "=", self.id)],
        }

    def action_view_records(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Records",
            "res_model": self.model_id.model,
            "view_type": "form",
            "view_mode": ",form,graph,pivot",
        }

    def open_action(self):
        self.env[self.model].check_access_rights("read")
        action = self.action_view_records()
        action["name"] = self.name
        action["domain"] = self._context.get("use_domain", [])
        return action

    def action_new_request(self):
        self.env[self.model].check_access_rights("create")
        ctx = self._context.copy()
        action = self.open_action()
        action.update({"view_mode": "form", "context": ctx})
        return action

    def action_details_model(self):
        access_ids = self.access_ids.read(
            [
                "name",
                "group_id",
                "perm_read",
                "perm_write",
                "perm_create",
                "perm_unlink",
            ],
            load=False,
        )
        for vals in access_ids:
            vals.pop("id")
        return {
            "type": "ir.actions.act_window",
            "name": "Details Model",
            "res_model": "ir.model",
            "view_mode": ",kanban,form",
            "domain": [("parent_approval_model_id", "=", self.id)],
            "context": {
                "default_parent_approval_model_id": self.id,
                "default_access_ids": access_ids,
            },
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "model_id" in vals:
                continue
            vals["is_approval_model"] = True
            vals["is_mail_thread"] = True
            vals["sequence_id"] = (
                self.env["ir.sequence"]
                .create(
                    {"name": vals["name"], "code": vals["model"], "company_id": False}
                )
                .id
            )
        records = super(ApprovalModel, self).create(vals_list)
        for record in records:
            record._insure_tree_fields()

        return records

    def _insure_tree_fields(self):
        if not self.tree_ids:
            for field in self.field_id.filtered(
                lambda field: field.name in ["name", "state"]
            ):
                self.write({"tree_ids": [(0, 0, {"field_id": field.id})]})

    @api.constrains("sequence_id")
    def _check_sequence(self):
        for record in self:
            if record.sequence_id and record.sequence_id.code != record.model:
                raise ValidationError(_("Invalid sequence code"))

    def _get_form_view_arch(self):
        res = []

        start_group = [0]

        def close_group():
            if start_group[0]:
                res.append("      </group>")
                start_group[0] = False

        for display in self.display_ids:
            if display.display_type == "line_section":
                close_group()
                res.append('      <group string="%s">' % (display.name or ""))
                start_group[0] = True
            else:
                res.append('        <field name="%s" />' % display.field_id.name)

        close_group()
        groups = "\n".join(res)

        res = []
        for page in self.page_ids:
            res.append('      <page string="%s">' % page.name)

            res.append('        <field name="%s" nolabel="1">' % page.field_id.name)

            res.append('          <list editable="%s">' % (page.editable or ""))
            for page_field in page.page_field_ids:
                res.append(
                    '          <field name="%s" invisible="%d" />'
                    % (page_field.field_id.name, page_field.tree_invisible)
                )
            res.append("          </list>")

            res.append("          <form>")
            res.append("            <group>")
            for page_field in page.page_field_ids:
                res.append(
                    '            <field name="%s" invisible="%d" />'
                    % (page_field.field_id.name, page_field.form_invisible)
                )
            res.append("            </group>")
            res.append("          </form>")

            res.append("        </field>")

            res.append("      </page>")

        pages = "\n".join(res)
        return _form_arch % {"groups": groups, "pages": pages}

    def _get_tree_view_arch(self):
        self._insure_tree_fields()

        res = []
        for tree_field in self.tree_ids:
            res.append('  <field name="%s" />' % tree_field.field_id.name)
        res = "\n".join(res)
        return _tree_arch % res

    def _get_search_view_arch(self):
        res = []
        for field in self.field_id.filtered(
            lambda field: field.name in ["x_subject", "x_description"]
        ):
            res.append('    <field name="%s" />' % field.name)
        res = "\n".join(res)
        return _search_arch % res

    def create_views(self):
        arch = self._get_form_view_arch()
        if self.form_view_id:
            self.form_view_id.write({"arch": arch})
        else:
            self.form_view_id = self.env["ir.ui.view"].create(
                {
                    "arch": arch,
                    "inherit_id": self.env.ref(
                        "eds_workflow_doc.view_approval_doc_form"
                    ).id,
                    "mode": "primary",
                    "name": "%s.form" % self.model,
                    "model": self.model,
                    "type": "form",
                }
            )

        arch = self._get_tree_view_arch()

        if self.tree_view_id:
            self.tree_view_id.write({"arch": arch})
        else:
            self.tree_view_id = self.env["ir.ui.view"].create(
                {
                    "arch": arch,
                    "mode": "primary",
                    "name": "%s.tree" % self.model,
                    "model": self.model,
                    "type": "tree",
                }
            )

        arch = self._get_search_view_arch()

        if self.search_view_id:
            self.search_view_id.write({"arch": arch})
        else:
            self.search_view_id = self.env["ir.ui.view"].create(
                {
                    "arch": arch,
                    "inherit_id": self.env.ref(
                        "eds_workflow_doc.view_approval_doc_search"
                    ).id,
                    "mode": "primary",
                    "name": "%s.search" % self.model,
                    "model": self.model,
                    "type": "search",
                }
            )

    def menu_create(self):
        if not self.menu_id:
            if not self.category_id.menu_id:
                self.category_id.menu_id = self.env["ir.ui.menu"].create(
                    {
                        "name": self.category_id.name,
                        "parent_id": self.env.ref(
                            "eds_workflow_doc.menu_approval_root"
                        ).id,
                    }
                )

            model = self.model_id
            vals = {
                "name": self.name,
                "res_model": model.model,
                "view_mode": ",form",
            }
            action_id = self.env["ir.actions.act_window"].create(vals)
            self.menu_id = self.env["ir.ui.menu"].create(
                {
                    "name": self.name,
                    "action": "ir.actions.act_window,%d" % (action_id,),
                    "parent_id": self.category_id.menu_id.id,
                }
            )
        return {
            "type": "ir.actions.act_window",
            "name": "Menu",
            "view_mode": "form",
            "res_model": "ir.ui.menu",
            "res_id": self.menu_id.id,
            "views": [(False, "form")],
        }
