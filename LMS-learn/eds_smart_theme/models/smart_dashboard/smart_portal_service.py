# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SmartPortalServiceCategory(models.Model):
    _name = "smart.portal.service.category"
    _description = "Smart Portal Service Category"
    _order = "sequence, id"

    name = fields.Char(string="Name", required=True, translate=True)
    code = fields.Char(
        string="Technical key",
        required=True,
        help="Unique key used for the dashboard tab (e.g. hr, finance).",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    item_ids = fields.One2many(
        "smart.portal.service.item",
        "category_id",
        string="Services",
    )
    item_count = fields.Integer(compute="_compute_item_count")

    _sql_constraints = [
        (
            "code_unique",
            "unique(code)",
            "The technical key must be unique per category.",
        ),
    ]

    @api.depends("item_ids")
    def _compute_item_count(self):
        for record in self:
            record.item_count = len(record.item_ids)

    @api.constrains("code")
    def _check_code(self):
        for record in self:
            code = (record.code or "").strip()
            if not code:
                raise ValidationError("The technical key is required.")
            if " " in code:
                raise ValidationError("The technical key must not contain spaces.")


class SmartPortalServiceItem(models.Model):
    _name = "smart.portal.service.item"
    _description = "Smart Portal Service Item"
    _order = "sequence, id"

    category_id = fields.Many2one(
        "smart.portal.service.category",
        string="Category",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(string="Name", required=True, translate=True)
    view_id = fields.Many2one(
        "ir.ui.view",
        string="Open view",
        ondelete="set null",
        help="When set, opens this Odoo view in the backend (preferred over Link).",
    )
    link_url = fields.Char(
        string="Link",
        help="External URL or internal path. Used only when Open view is empty.",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    @api.constrains("view_id", "link_url")
    def _check_navigation_target(self):
        for record in self:
            if record.view_id:
                continue
            if not (record.link_url or "").strip():
                raise ValidationError(
                    "Set either Open view or Link for each self-service item."
                )

    def _resolve_form_view_for_portal(self, view):
        """Pair a portal tree/kanban view with the matching form view."""
        if not view or view.type == "form":
            return view
        View = self.env["ir.ui.view"].sudo()
        external_ids = view.get_external_id()
        xmlid = external_ids.get(view.id, "")
        if xmlid and "." in xmlid:
            module, name = xmlid.split(".", 1)
            candidates = []
            for suffix in ("_tree_view", "_tree", "_kanban"):
                if name.endswith(suffix):
                    base = name[: -len(suffix)]
                    candidates.extend(
                        [
                            f"{base}_form_view",
                            f"{base}_form",
                            f"{base}_service_form",
                        ]
                    )
                    break
            for candidate in candidates:
                form_view = self.env.ref(
                    f"{module}.{candidate}", raise_if_not_found=False
                )
                if form_view and form_view.type == "form":
                    return form_view
        if "approval.model" in self.env:
            approval = (
                self.env["approval.model"]
                .sudo()
                .search([("model_id.model", "=", view.model)], limit=1)
            )
            if approval and approval.form_view_id:
                return approval.form_view_id
        form_views = View.search(
            [
                ("model", "=", view.model),
                ("type", "=", "form"),
                ("active", "=", True),
            ],
            order="priority asc, id asc",
        )
        primary = form_views.filtered(lambda v: v.mode == "primary")
        return (primary or form_views)[:1]

    def _approval_model_base_action(self, model_name):
        if "approval.model" not in self.env:
            return None
        approval = (
            self.env["approval.model"]
            .sudo()
            .search([("model_id.model", "=", model_name)], limit=1)
        )
        if not approval:
            return None
        try:
            return dict(approval.open_action())
        except Exception:
            return None

    def _get_portal_open_action(self):
        self.ensure_one()
        if not self.view_id:
            return None
        view = self.view_id
        view_type = view.type or "form"
        action = self._approval_model_base_action(view.model) or {
            "type": "ir.actions.act_window",
            "res_model": view.model,
        }
        action.update(
            {
                "type": "ir.actions.act_window",
                "name": self.name,
                "res_model": view.model,
                "target": "current",
            }
        )
        if view_type == "form":
            action["view_mode"] = "form"
            action["views"] = [(view.id, "form")]
            return action
        if view_type in ("tree", "kanban"):
            views = [(view.id, view_type)]
            view_modes = [view_type]
            form_view = self._resolve_form_view_for_portal(view)
            if form_view:
                views.append((form_view.id, "form"))
                view_modes.append("form")
            action["views"] = views
            action["view_mode"] = ",".join(view_modes)
            return action
        action["view_mode"] = view_type
        action["views"] = [(view.id, view_type)]
        return action
