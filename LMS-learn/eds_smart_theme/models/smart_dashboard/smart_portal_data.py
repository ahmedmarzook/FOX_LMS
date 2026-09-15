# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.addons.web.controllers.utils import clean_action
from odoo.osv import expression

# Hourly leave type on portal (legacy website layout).
_HOURLY_LEAVE_TYPE_ID = 62
_PERMISSION_LEAVE_TYPE_ID = 22
_MONTHLY_REMOTE_WORK_DAYS = 3
_MONTHLY_PERMISSION_MINUTES = 8 * 60
_ANNUAL_PERMISSION_MINUTES = 48 * 60
_REMOTE_WORK_LABEL_MARKERS = (
    "remote work",
    "work from home",
    "العمل عن بعد",
    "عمل عن بعد",
)
_MONTHLY_PERMISSION_MARKERS = (
    "monthly permission",
    "استئذان شهري",
    "permission monthly",
)
_ANNUAL_LEAVE_MARKERS = (
    "annual leave",
    "leave balance",
    "الإجازة السنوية",
    "سنوية",
)
_EMERGENCY_LEAVE_MARKERS = (
    "emergency",
    "اضطرار",
    "اضطرارية",
)
_ANNUAL_PERMISSION_MARKERS = (
    "annual permission",
    "استئذان سنوي",
    "permission annual",
)

# Fixed KPI row order must match getKpiSlots() in smart_dashboard.js.
_KPI_SLOT_COUNT = 5

_AR_MONTHS = [
    "يناير",
    "فبراير",
    "مارس",
    "أبريل",
    "مايو",
    "يونيو",
    "يوليو",
    "أغسطس",
    "سبتمبر",
    "أكتوبر",
    "نوفمبر",
    "ديسمبر",
]

_EVENT_COLORS = ("#286fd4", "#f3bb22")

# approval.log tracks state changes for ~270 models (per approval.settings),
# but not all of them are employee-submitted requests — these are asset
# custody/inventory bookkeeping records that happen to carry employee_id.
_APPROVAL_LOG_EXCLUDED_MODELS = {
    "account.asset",
    "hr.payslip",
    "hr.leave.allocation",
    "account.asset.movement",
    "account.asset.exclusion",
    "account.asset.sell",
    "account.asset.benefactor",
    "asset.count",
    "asset.count.inventory",
    "asset.diffrance.inventory",
}

# Terminal-state vocabulary fallback for models with no approval.settings.state
# configured (so show_approved_request never becomes True for them) — covers
# the conventional state codes those models reuse.
_APPROVAL_LOG_REJECTED_STATES = {"refuse", "refused", "rejected"}
_APPROVAL_LOG_CANCELLED_STATES = {"cancel", "canceled", "cancelled"}
_APPROVAL_LOG_APPROVED_STATES = {
    "approved",
    "validate",
    "closed",
    "close",
    "done",
    "resolved",
    "paid",
}
_APPROVAL_LOG_DRAFT_STATES = {"draft"}


class ShSmartPortalData(models.AbstractModel):
    _name = "smart.portal.data"
    _description = "Smart Portal Dashboard Data"

    # ------------------------------------------------------------------ blog
    @api.model
    def _published_blog_domain(self, blog_code=None, extra_domain=None):
        now = fields.Datetime.now()
        domain = [
            ("state", "=", "publish"),
            "|",
            ("post_date", "=", False),
            ("post_date", "<=", now),
            "|",
            ("unpost_date", "=", False),
            ("unpost_date", ">=", now),
        ]
        if blog_code:
            domain = expression.AND([domain, [("blog_id.code", "=", blog_code)]])
        if extra_domain:
            domain = expression.AND([domain, extra_domain])
        return domain

    @api.model
    def _format_post_date(self, post_date):
        if not post_date:
            return ""
        if isinstance(post_date, datetime):
            dt = post_date
        else:
            dt = datetime.combine(post_date, datetime.min.time())
        return f"{dt.day} {_AR_MONTHS[dt.month - 1]} {dt.year}"

    @api.model
    def _blog_post_url(self, post):
        if hasattr(post, "website_url") and post.website_url:
            return post.website_url
        if post.blog_id:
            return f"/blog/{post.blog_id.id}/post/{post.id}"
        return ""

    @api.model
    def _blog_post_image_url(self, post):
        # Build URL only; do not read binary (broken filestore files must not break bootstrap).
        if "image_512" in post._fields:
            return f"/web/image/blog.post/{post.id}/image_512"
        if "image" in post._fields:
            return f"/web/image/blog.post/{post.id}/image"
        return "/web/static/img/placeholder.png"

    @api.model
    def _serialize_blog_post(self, post, *, dot_color=None):
        display_date = post.post_date
        blog_code = post.blog_id.code if post.blog_id else ""
        if getattr(post, "press_news_date", None) and blog_code == "press":
            display_date = post.press_news_date or display_date
        return {
            "id": post.id,
            "title": post.name or "",
            "subtitle": post.subtitle or "",
            "date": self._format_post_date(display_date),
            "image_url": self._blog_post_image_url(post),
            "blog_code": post.blog_id.code if post.blog_id else "",
            "url": self._blog_post_url(post),
            "dot": dot_color or _EVENT_COLORS[post.id % len(_EVENT_COLORS)],
        }

    @api.model
    def _blog_search_domain(self, search=None):
        query = (search or "").strip()
        if not query:
            return []
        return [
            "|",
            ("name", "ilike", query),
            ("subtitle", "ilike", query),
        ]

    @api.model
    def get_news_posts(self, limit=5, search=None):
        domain = expression.OR(
            [
                [("blog_id.code", "=", "news")],
                [("is_news", "=", True)],
            ]
        )
        domain = expression.AND([self._published_blog_domain(), domain])
        search_domain = self._blog_search_domain(search)
        if search_domain:
            domain = expression.AND([domain, search_domain])
            limit = max(limit or 0, 50)
        posts = (
            self.env["blog.post"]
            .sudo()
            .search(domain, order="post_date desc", limit=limit)
        )
        return [self._serialize_blog_post(p) for p in posts]

    @api.model
    def get_decisions(self, limit=6, search=None):
        domain = self._published_blog_domain("decisions")
        search_domain = self._blog_search_domain(search)
        if search_domain:
            domain = expression.AND([domain, search_domain])
            limit = max(limit or 0, 50)
        posts = (
            self.env["blog.post"]
            .sudo()
            .search(domain, order="post_date desc", limit=limit)
        )
        return [self._serialize_blog_post(p) for p in posts]

    @api.model
    def get_press_news(self, limit=3, search=None):
        domain = self._published_blog_domain("press")
        search_domain = self._blog_search_domain(search)
        if search_domain:
            domain = expression.AND([domain, search_domain])
            limit = max(limit or 0, 50)
        posts = (
            self.env["blog.post"]
            .sudo()
            .search(domain, order="post_date desc", limit=limit)
        )
        return [self._serialize_blog_post(p) for p in posts]

    @api.model
    def get_employee_news(self, limit=5, search=None):
        domain = self._published_blog_domain("employee")
        search_domain = self._blog_search_domain(search)
        querying = bool(search_domain)
        if querying:
            domain = expression.AND([domain, search_domain])
            limit = max(limit or 0, 50)
        posts = (
            self.env["blog.post"]
            .sudo()
            .search(
                domain, order="post_date desc", limit=limit if querying else limit * 3
            )
        )
        if not querying:
            now = fields.Datetime.now()
            posts = posts.filtered(
                lambda p: p.post_date and p.post_date + timedelta(days=5) >= now
            )
        result = []
        for post in posts[:limit]:
            item = self._serialize_blog_post(post, dot_color="#24d4bc")
            emp = post.employee_id
            if emp:
                item.update(
                    {
                        "employee_id": emp.id,
                        "employee_name": emp.name or "",
                        "employee_department": emp.department_id.name or "",
                        "job_title": emp.job_id.name or "",
                        "image_url": self._employee_image_url(emp),
                    }
                )
            result.append(item)
        return result

    @api.model
    def get_new_joiners(self, limit=5):
        posts = (
            self.env["blog.post"]
            .sudo()
            .search(
                self._published_blog_domain("join"),
                order="post_date desc",
                limit=limit,
            )
        )
        result = []
        for post in posts:
            emp = post.employee_id
            result.append(
                {
                    "id": post.id,
                    "title": post.name or "",
                    "subtitle": post.subtitle or "",
                    "post_date": (
                        fields.Date.to_string(post.post_date) if post.post_date else ""
                    ),
                    "url": (
                        f"/blog/{post.blog_id.id}/post/{post.id}"
                        if post.blog_id
                        else ""
                    ),
                    "employee_id": emp.id if emp else False,
                    "employee_name": emp.name if emp else (post.name or ""),
                    "department": (
                        emp.department_id.name if emp and emp.department_id else ""
                    ),
                    "job_title": emp.job_id.name if emp and emp.job_id else "",
                    "image_url": (
                        self._employee_image_url(emp)
                        if emp
                        else f"/web/image/blog.post/{post.id}/image_512"
                    ),
                }
            )
        return result

    # ------------------------------------------------------------------ HR
    @api.model
    def _employee_image_url(self, employee):
        if not employee:
            return "/web/static/img/placeholder.png"
        return f"/web/image/hr.employee/{employee.id}/avatar_128"

    @api.model
    def _serialize_action(self, action):
        if not action or not isinstance(action, dict):
            return None
        return clean_action(dict(action), self.env)

    @api.model
    def _get_employee(self, user=None):
        user = user or self.env.user
        if "hr.employee" not in self.env:
            return self.env["hr.employee"]
        return (
            self.env["hr.employee"].sudo().search([("user_id", "=", user.id)], limit=1)
        )

    @api.model
    def get_profile(self, employee=None):
        employee = employee or self._get_employee()
        if not employee:
            partner = self.env.user.partner_id
            return {
                "name": partner.name or "",
                "department": "",
                "job_title": "",
                "employee_no": "",
                "grade": "",
                "avatar_url": f"/web/image/res.partner/{partner.id}/avatar_128",
                "tenure_label": "",
            }
        tenure_label = ""
        if "hr.end_of_service" in self.env:
            eos = (
                self.env["hr.end_of_service"]
                .sudo()
                .new(
                    {
                        "employee_id": employee.id,
                        "date": fields.Date.context_today(self),
                    }
                )
            )
            if eos.service_desc:
                tenure_label = (
                    eos.service_desc.replace(",", "،")
                    .replace("Years", "سنوات")
                    .replace("Months", "أشهر")
                    .replace("Days", "أيام")
                )
        grade = ""
        if getattr(employee, "grade_id", None):
            grade = employee.grade_id.name or ""
        employee_no = (
            getattr(employee, "employee_no", None)
            or getattr(employee, "barcode", None)
            or getattr(employee, "identification_id", None)
            or str(employee.id)
        )
        return {
            "name": employee.name or "",
            "department": employee.department_id.name if employee.department_id else "",
            "job_title": employee.job_title
            or (employee.job_id.name if employee.job_id else ""),
            "employee_no": employee_no or "",
            "grade": grade,
            "avatar_url": self._employee_image_url(employee),
            "tenure_label": tenure_label,
        }

    @api.model
    def _permission_label_matches(self, leave_type, label, markers):
        texts = [
            (label or "").lower(),
            (getattr(leave_type, "portal_name", None) or "").lower(),
            (leave_type.name or "").lower(),
            (getattr(leave_type, "code", None) or "").lower(),
        ]
        return any(marker in text for text in texts for marker in markers)

    @api.model
    def _is_monthly_permission_leave_type(self, leave_type, label=""):
        if self._permission_label_matches(
            leave_type, label, _ANNUAL_PERMISSION_MARKERS
        ):
            return False
        return self._permission_label_matches(
            leave_type, label, _MONTHLY_PERMISSION_MARKERS
        )

    @api.model
    def _is_annual_permission_leave_type(self, leave_type, label=""):
        return self._permission_label_matches(
            leave_type, label, _ANNUAL_PERMISSION_MARKERS
        )

    @api.model
    def _format_permission_hours_value(self, remaining_minutes):
        remaining_minutes = max(0, int(remaining_minutes))
        hours = remaining_minutes // 60
        minutes = remaining_minutes % 60
        return f"{hours}:{minutes:02d}"

    @api.model
    def _get_permission_hours_remaining(self, employee):
        """Same logic as jes_holidays.hr.leave.get_permission_hours."""
        if not employee or "hr.leave" not in self.env:
            return {"month": "0:00", "year": "0:00"}
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        month_end = month_start + relativedelta(months=1, days=-1)
        year_start = today.replace(month=1, day=1)
        year_end = today.replace(month=12, day=31)
        Leave = self.env["hr.leave"].sudo()
        base_domain = [
            ("holiday_status_id.id", "=", _PERMISSION_LEAVE_TYPE_ID),
            ("employee_id", "=", employee.id),
            ("state", "not in", ["draft", "refuse", "cancel"]),
        ]
        month_leaves = Leave.search(
            base_domain
            + [
                ("request_date_from", ">=", month_start),
                ("request_date_from", "<=", month_end),
            ]
        )
        year_leaves = Leave.search(
            base_domain
            + [
                ("request_date_from", ">=", year_start),
                ("request_date_from", "<=", year_end),
            ]
        )
        used_minutes_month = int(
            sum(month_leaves.mapped("number_of_hours_display")) * 60
        )
        used_minutes_year = int(sum(year_leaves.mapped("number_of_hours_display")) * 60)
        return {
            "month": self._format_permission_hours_value(
                _MONTHLY_PERMISSION_MINUTES - used_minutes_month
            ),
            "year": self._format_permission_hours_value(
                _ANNUAL_PERMISSION_MINUTES - used_minutes_year
            ),
        }

    @api.model
    def _is_remote_work_leave_type(self, leave_type, label=""):
        texts = [
            (label or "").lower(),
            (getattr(leave_type, "portal_name", None) or "").lower(),
            (leave_type.name or "").lower(),
            (getattr(leave_type, "code", None) or "").lower(),
        ]
        return any(
            marker in text for text in texts for marker in _REMOTE_WORK_LABEL_MARKERS
        )

    @api.model
    def _get_remote_work_remaining_days(self, employee):
        """Same logic as work.form.home.service._compute_available_days (3 days/month)."""
        if not employee or "work.form.home.service" not in self.env:
            return 0
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        month_end = month_start + relativedelta(months=1) - timedelta(days=1)
        approved_count = (
            self.env["work.form.home.service"]
            .sudo()
            .search_count(
                [
                    ("requester_id", "=", employee.id),
                    ("state", "not in", ["draft", "rejected", "canceled"]),
                    ("work_date", ">=", month_start),
                    ("work_date", "<=", month_end),
                ]
            )
        )
        return max(0, _MONTHLY_REMOTE_WORK_DAYS - approved_count)

    @api.model
    def _leave_type_remaining(self, employee, leave_type):
        if not hasattr(leave_type, "get_allocation_data"):
            return 0.0
        data_days = leave_type.get_allocation_data(employee).get(employee, [])
        for item in data_days:
            if len(item) > 3 and item[3] == leave_type.id:
                return item[1].get("remaining_leaves", 0) or 0
        for item in data_days:
            if item[0] == leave_type.name:
                return item[1].get("remaining_leaves", 0) or 0
        if len(data_days) == 1:
            return data_days[0][1].get("remaining_leaves", 0) or 0
        return 0.0

    @api.model
    def _portal_leave_type_label(self, leave_type, lang=None):
        lang = lang or self.env.lang or "en_US"
        return (
            leave_type.with_context(lang=lang).portal_name
            or leave_type.with_context(lang=lang).name
        )

    @api.model
    def _is_special_kpi_leave_type(self, leave_type, label=""):
        return (
            self._is_remote_work_leave_type(leave_type, label)
            or self._is_monthly_permission_leave_type(leave_type, label)
            or self._is_annual_permission_leave_type(leave_type, label)
        )

    @api.model
    def _find_portal_leave_type(self, portal_types, markers, exclude_markers=()):
        for leave_type in portal_types:
            label = self._portal_leave_type_label(leave_type)
            if exclude_markers and self._permission_label_matches(
                leave_type, label, exclude_markers
            ):
                continue
            if self._permission_label_matches(leave_type, label, markers):
                return leave_type
        return None

    @api.model
    def _resolve_annual_emergency_leave_types(self, portal_types):
        annual = self._find_portal_leave_type(
            portal_types, _ANNUAL_LEAVE_MARKERS, _EMERGENCY_LEAVE_MARKERS
        )
        emergency = self._find_portal_leave_type(portal_types, _EMERGENCY_LEAVE_MARKERS)
        standard = []
        for leave_type in portal_types:
            label = self._portal_leave_type_label(leave_type)
            if self._is_special_kpi_leave_type(leave_type, label):
                continue
            standard.append(leave_type)
        if not annual and standard:
            annual = standard[0]
        if not emergency:
            for leave_type in standard:
                if leave_type != annual:
                    emergency = leave_type
                    break
        return annual, emergency

    @api.model
    def _format_leave_type_kpi_value(self, employee, leave_type):
        remaining = self._leave_type_remaining(employee, leave_type)
        if (
            leave_type.id == _HOURLY_LEAVE_TYPE_ID
            or getattr(leave_type, "request_unit", None) == "hour"
        ):
            hours = int(remaining)
            minutes = int(round((remaining - hours) * 60))
            return f"{hours}:{minutes:02d}", "hours"
        return str(remaining), "days"

    @api.model
    def get_leave_kpis(self, employee=None):
        employee = employee or self._get_employee()
        if not employee:
            return []
        lang = self.env.lang or "en_US"
        permission_hours = self._get_permission_hours_remaining(employee)
        remote_days = self._get_remote_work_remaining_days(employee)

        annual_type = emergency_type = None
        LeaveType = self.env["hr.leave.type"].sudo()
        if "is_portal" in LeaveType._fields:
            portal_types = LeaveType.search(
                [("is_portal", "=", True)], order="sequence, id"
            )
            annual_type, emergency_type = self._resolve_annual_emergency_leave_types(
                portal_types
            )

        kpis = []
        if annual_type:
            value, unit = self._format_leave_type_kpi_value(employee, annual_type)
            kpis.append(
                {
                    "id": annual_type.id,
                    "label": self._portal_leave_type_label(annual_type, lang),
                    "value": value,
                    "unit": unit,
                }
            )
        else:
            kpis.append(
                {
                    "id": 0,
                    "label": _("Leave balance"),
                    "value": "0",
                    "unit": "days",
                }
            )

        if emergency_type:
            value, unit = self._format_leave_type_kpi_value(employee, emergency_type)
            kpis.append(
                {
                    "id": emergency_type.id,
                    "label": self._portal_leave_type_label(emergency_type, lang),
                    "value": value,
                    "unit": unit,
                }
            )
        else:
            kpis.append(
                {
                    "id": 0,
                    "label": _("Emergency leave balance"),
                    "value": "0",
                    "unit": "days",
                }
            )

        kpis.extend(
            [
                {
                    "id": 0,
                    "label": _("Remote work"),
                    "value": str(remote_days),
                    "unit": "days",
                },
                {
                    "id": _PERMISSION_LEAVE_TYPE_ID,
                    "label": _("Monthly permission"),
                    "value": permission_hours["month"],
                    "unit": "hours",
                },
                {
                    "id": _PERMISSION_LEAVE_TYPE_ID,
                    "label": _("Annual permission"),
                    "value": permission_hours["year"],
                    "unit": "hours",
                },
            ]
        )
        return kpis[:_KPI_SLOT_COUNT]

    # ------------------------------------------------------------------ tasks
    @api.model
    def _tasks_requests_since_datetime(self):
        return fields.Datetime.now() - relativedelta(years=1)

    @api.model
    def _record_row_action(self, model_name, record_id):
        log = (
            self.env["approval.log"]
            .sudo()
            .search(
                [
                    ("model_id.model", "=", model_name),
                    ("record_id", "=", record_id),
                ],
                limit=1,
                order="id desc",
            )
        )
        if log and hasattr(log, "action_view_record"):
            try:
                return self._serialize_action(log.action_view_record())
            except Exception:
                pass
        if model_name not in self.env:
            return None
        record = self.env[model_name].browse(record_id)
        if not record.exists():
            return None
        return self._serialize_action(
            {
                "type": "ir.actions.act_window",
                "res_model": model_name,
                "view_mode": "form",
                "res_id": record_id,
                "target": "current",
            }
        )

    @api.model
    def _approval_log_owner_capable_models(self):
        """Models with employee_id/requester_id — approval.log rows on any
        other model (account.move, account.payment, ...) can never match."""
        return [
            name
            for name, model_cls in self.env.registry.items()
            if name not in _APPROVAL_LOG_EXCLUDED_MODELS
            and (
                "employee_id" in model_cls._fields
                or "requester_id" in model_cls._fields
            )
        ]

    @api.model
    def _approval_log_candidate_ids_by_model(self, since):
        """{model_name: {record_id}} for approval.log rows since `since`,
        restricted to owner-capable models. Raw SQL: at 100k+ matching rows,
        ORM record marshalling (search/read) dominates cost — this is a plain
        (model, record_id) column scan."""
        owner_models = self._approval_log_owner_capable_models()
        if not owner_models:
            return {}
        self.env.cr.execute(
            """
            SELECT im.model, al.record_id
            FROM approval_log al
            JOIN ir_model im ON im.id = al.model_id
            WHERE im.model = ANY(%s) AND al.date >= %s
            """,
            (owner_models, since),
        )
        grouped = defaultdict(set)
        for model_name, record_id in self.env.cr.fetchall():
            grouped[model_name].add(record_id)
        return grouped

    @api.model
    def _employee_owned_record_ids(self, model_name, record_ids, employee):
        """One indexed search per model instead of browsing each record."""
        if not record_ids or model_name not in self.env:
            return set()
        Model = self.env[model_name].sudo()
        owner_fields = [
            f for f in ("employee_id", "requester_id") if f in Model._fields
        ]
        if not owner_fields:
            return set()
        owner_domain = expression.OR([[(f, "=", employee.id)] for f in owner_fields])
        domain = expression.AND([[("id", "in", list(record_ids))], owner_domain])
        return set(Model.search(domain).ids)

    @api.model
    def _approval_log_bucket(self, log):
        """Classify a (deduped, latest-per-record) log as 'pending',
        'approved' or 'dropped' (draft/rejected/cancelled — shown in
        neither list). Combines the settings-driven show_approved_request
        flag (correct when approval.settings.state is configured for the
        model) with a literal terminal-state fallback for models without
        that configuration, which conventionally reuse the same codes."""
        state = (log.state or "").lower()
        if (
            state in _APPROVAL_LOG_REJECTED_STATES
            or state in _APPROVAL_LOG_CANCELLED_STATES
        ):
            return "dropped"
        if state in _APPROVAL_LOG_DRAFT_STATES:
            return "dropped"
        if log.show_approved_request or state in _APPROVAL_LOG_APPROVED_STATES:
            return "approved"
        return "pending"

    @api.model
    def _approval_logs_for_employee(self, employee, bucket, since, limit):
        """Approval logs classified as `bucket` on records owned by
        `employee` (via employee_id/requester_id), newest first, capped at
        `limit`. log.user_id = env.uid only decides which records qualify
        (the current user must have personally logged an action on it at
        least once) — the displayed bucket/status always comes from that
        record's true latest log, not a stale snapshot of the user's own
        last action, since someone else (an approver) may have moved it
        further since then."""
        if not employee:
            return self.env["approval.log"]
        candidates = self._approval_log_candidate_ids_by_model(since)
        owned_domains = []
        for model_name, record_ids in candidates.items():
            owned_ids = self._employee_owned_record_ids(
                model_name, record_ids, employee
            )
            if owned_ids:
                owned_domains.append(
                    expression.AND(
                        [
                            [("model_id.model", "=", model_name)],
                            [("record_id", "in", list(owned_ids))],
                        ]
                    )
                )
        if not owned_domains:
            return self.env["approval.log"]
        owned_domain = expression.AND(
            [[("date", ">=", since)], expression.OR(owned_domains)]
        )
        Log = self.env["approval.log"].sudo()
        acted_domain = expression.AND([owned_domain, [("user_id", "=", self.env.uid)]])
        acted_logs = Log.search(acted_domain)
        acted_keys = {(log.model_id.id, log.record_id) for log in acted_logs}
        if not acted_keys:
            return self.env["approval.log"]
        logs = Log.search(owned_domain, order="date desc, id desc")
        logs = self._dedupe_approval_logs(logs)
        logs = logs.filtered(
            lambda log: (log.model_id.id, log.record_id) in acted_keys
            and self._approval_log_bucket(log) == bucket
        )
        return logs[:limit]

    @api.model
    def _dedupe_approval_logs(self, logs):
        """Keep one log per (model_id, record_id) — highest id wins; newest first."""
        if not logs:
            return logs
        best_by_key = {}
        for log in logs:
            key = (log.model_id.id, log.record_id)
            if key not in best_by_key or log.id > best_by_key[key].id:
                best_by_key[key] = log

        def sort_key(log):
            value = log.date
            if not value:
                stamp = datetime.min
            elif isinstance(value, datetime):
                stamp = value
            else:
                stamp = datetime.combine(value, datetime.min.time())
            return (stamp, log.id)

        kept = sorted(best_by_key.values(), key=sort_key, reverse=True)
        return logs.browse([log.id for log in kept])

    @api.model
    def _sort_rows_newest_first(self, rows):
        """Ensure portal table rows keep newest records at the top."""
        return sorted(
            rows,
            key=lambda row: int(row.get("id") or 0),
            reverse=True,
        )

    @api.model
    def _linked_service_record(self, model_name, record_id):
        if not model_name or not record_id or model_name not in self.env:
            return None
        try:
            record = self.env[model_name].sudo().browse(record_id)
            return record if record.exists() else None
        except Exception:
            return None

    @api.model
    def _field_selection_label(self, record, field_name):
        if field_name not in record._fields:
            return ""
        value = record[field_name]
        if not value:
            return ""
        field = record._fields[field_name]
        if field.type == "selection":
            selection = dict(field._description_selection(record.env))
            return selection.get(value, value) or ""
        return str(value)

    @api.model
    def _many2one_label(self, record, field_name):
        if field_name not in record._fields:
            return ""
        value = record[field_name]
        if not value:
            return ""
        label_ar = (value.sudo().with_context(lang="ar_001").display_name or "").strip()
        if label_ar:
            return label_ar
        return value.display_name or ""

    @api.model
    def _format_owner_display_name(self, full_name):
        parts = [part for part in (full_name or "").split() if part]
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0]
        return f"{parts[0]} {parts[-1]}"

    @api.model
    def _employee_name_prefer_arabic(self, employee):
        if not employee:
            return ""
        employee = employee.sudo()
        name_ar = (employee.with_context(lang="ar_001").name or "").strip()
        if name_ar:
            return self._format_owner_display_name(name_ar)
        name_en = (employee.with_context(lang="en_US").name or "").strip()
        full_name = name_en or (employee.name or "").strip()
        return self._format_owner_display_name(full_name)

    @api.model
    def _model_display_name_ar(self, model_record):
        if not model_record:
            return ""
        model_record = model_record.sudo()
        name_ar = (model_record.with_context(lang="ar_001").name or "").strip()
        if name_ar:
            return name_ar
        return model_record.display_name or ""

    @api.model
    def _user_owner_name(self, user):
        if not user:
            return ""
        employee = user.employee_id
        if not employee and "employee_ids" in user._fields:
            employee = user.employee_ids[:1]
        name = self._employee_name_prefer_arabic(employee)
        if name:
            return name
        return self._format_owner_display_name(user.name or "")

    @api.model
    def _activity_requester_name(self, record):
        if "create_uid" not in record._fields or not record.create_uid:
            return ""
        return self._employee_name_prefer_arabic(record.create_uid)

    @api.model
    def _approval_log_requester_name(self, record):
        if "requester_id" not in record._fields or not record.requester_id:
            return ""
        return self._employee_name_prefer_arabic(record.requester_id)

    @api.model
    def _activity_table_columns(
        self,
        model_name,
        record_id,
        *,
        title_fallback="",
        status_fallback="",
        owner_fallback="",
    ):
        """Map table cells from linked service record fields for a mail.activity row."""
        try:
            record = self._linked_service_record(model_name, record_id)
            if not record:
                return title_fallback, status_fallback, owner_fallback
            title = self._many2one_label(record, "name") or title_fallback
            if "state_name" in record._fields and record.state_name:
                status = record.state_name
            else:
                status = self._field_selection_label(record, "state") or status_fallback
            owner = self._activity_requester_name(record) or owner_fallback
            return title, status, owner
        except Exception:
            return title_fallback, status_fallback, owner_fallback

    @api.model
    def _approval_log_table_columns(
        self,
        model_name,
        record_id,
        *,
        title_fallback="",
        status_fallback="",
        owner_fallback="",
    ):
        """Map table cells from linked service record fields for an approval.log row."""
        try:
            record = self._linked_service_record(model_name, record_id)
            if not record:
                return title_fallback, status_fallback, owner_fallback
            title = self._many2one_label(record, "name") or title_fallback
            if "state_name" in record._fields and record.state_name:
                status = record.state_name
            else:
                status = self._field_selection_label(record, "state") or status_fallback
            owner = self._approval_log_requester_name(record) or owner_fallback
            return title, status, owner
        except Exception:
            return title_fallback, status_fallback, owner_fallback

    @api.model
    def _approval_log_service_name(self, log):
        """Fallback service label when linked record has no type_id."""
        return log.model_id.name if log.model_id else ""

    @api.model
    def _activity_state_label(self, activity):
        state_field = activity._fields.get("state")
        if not state_field or not state_field.selection:
            return activity.state or ""
        selection = dict(state_field._description_selection(activity.env))
        return selection.get(activity.state, activity.state or "")

    @api.model
    def _activity_can_approve(self, activity):
        """Whether the current user may approve via this activity's linked record."""
        try:
            if not activity.res_model or not activity.res_id:
                return False
            if activity.res_model not in self.env:
                return False
            # sudo read: assignee may lack direct record ACL; approval flags still
            # evaluate against env.user inside oi_workflow compute methods.
            record = self.env[activity.res_model].sudo().browse(activity.res_id)
            if not record.exists():
                return False
            if "button_approve_enabled" in record._fields:
                return bool(record.button_approve_enabled)
            if (
                hasattr(record, "action_approve")
                and activity.user_id.id == self.env.uid
            ):
                return True
        except Exception:
            return False
        return False

    @api.model
    def _mail_activity_row(self, activity):
        model_name = activity.res_model or ""
        record_id = activity.res_id or False
        title_fallback = self._model_display_name_ar(activity.res_model_id)
        status_fallback = self._activity_state_label(activity)
        owner_fallback = self._user_owner_name(activity.create_uid)
        title, status, owner = self._activity_table_columns(
            model_name,
            record_id,
            title_fallback=title_fallback,
            status_fallback=status_fallback,
            owner_fallback=owner_fallback,
        )
        action = None
        if hasattr(activity, "action_view_record"):
            try:
                action = self._serialize_action(activity.action_view_record())
            except Exception:
                pass
        if not action and activity.res_model and activity.res_id:
            action = self._record_row_action(activity.res_model, activity.res_id)
        return {
            "id": activity.id,
            "res_model": activity.res_model or "",
            "res_id": activity.res_id or False,
            "can_approve": self._activity_can_approve(activity),
            "code": activity.res_name or "",
            "title": title,
            "status": status,
            "statusKey": "pending",
            "owner": owner,
            "action": action,
        }

    @api.model
    def approve_pending_activity(self, activity_id):
        activity = self.env["mail.activity"].search(
            [("id", "=", activity_id), ("user_id", "=", self.env.uid)],
            limit=1,
        )
        if not activity:
            return {
                "success": False,
                "message": _("Activity not found or access denied."),
            }
        if not activity.res_model or not activity.res_id:
            return {"success": False, "message": _("This activity cannot be approved.")}
        if activity.res_model not in self.env:
            return {"success": False, "message": _("This activity cannot be approved.")}
        record = self.env[activity.res_model].browse(activity.res_id)
        if not record.exists():
            return {
                "success": False,
                "message": _("The linked record no longer exists."),
            }
        if "button_approve_enabled" in record._fields:
            if not record.button_approve_enabled:
                return {
                    "success": False,
                    "message": _("You are not allowed to approve this request."),
                }
            if record.approve_button_wizard:
                return {
                    "success": False,
                    "action": self._serialize_action(record.action_approve_wizard()),
                }
            result = record.action_approve()
            if isinstance(result, dict) and result.get("type"):
                return {"success": False, "action": self._serialize_action(result)}
            return {"success": True, "message": _("Request approved successfully.")}
        if hasattr(record, "action_approve") and activity.user_id.id == self.env.uid:
            result = record.action_approve()
            if isinstance(result, dict) and result.get("type"):
                return {"success": False, "action": self._serialize_action(result)}
            return {"success": True, "message": _("Request approved successfully.")}
        return {"success": False, "message": _("This activity cannot be approved.")}

    @api.model
    def _approval_log_row(self, log, *, default_status_key="pending"):
        creator = log.creator_uid
        owner_fallback = self._user_owner_name(creator)
        status_fallback = log.name or log.state or ""
        if log.show_approved_request or log.show_completed_request:
            status_key = "closed"
        else:
            status_key = default_status_key
        code = log.res_name or str(log.record_id)
        model_name = log.model_id.model if log.model_id else False
        title_fallback = self._approval_log_service_name(log)
        title, status, owner = self._approval_log_table_columns(
            model_name,
            log.record_id,
            title_fallback=title_fallback,
            status_fallback=status_fallback,
            owner_fallback=owner_fallback,
        )
        action = (
            self._record_row_action(model_name, log.record_id) if model_name else None
        )
        return {
            "id": log.id,
            "code": code,
            "title": title,
            "status": status,
            "statusKey": status_key,
            "owner": owner,
            "action": action,
        }

    @api.model
    def _approval_log_rows(self, logs, *, default_status_key="pending"):
        rows = []
        for log in logs:
            try:
                rows.append(
                    self._approval_log_row(log, default_status_key=default_status_key)
                )
            except Exception:
                continue
        return rows

    @api.model
    def get_pending_activities(self, limit=1000):
        if "mail.activity" not in self.env:
            return []
        uid = self.env.uid
        since = self._tasks_requests_since_datetime()
        activities = (
            self.env["mail.activity"]
            .sudo()
            .search(
                [("user_id", "=", uid), ("create_date", ">=", since)],
                limit=limit,
                order="create_date desc, id desc",
            )
        )
        rows = []
        for activity in activities:
            try:
                rows.append(self._mail_activity_row(activity))
            except Exception:
                rows.append(
                    {
                        "id": activity.id,
                        "res_model": activity.res_model or "",
                        "res_id": activity.res_id or False,
                        "can_approve": False,
                        "code": activity.res_name or "",
                        "title": self._model_display_name_ar(activity.res_model_id),
                        "status": self._activity_state_label(activity),
                        "statusKey": "pending",
                        "owner": self._user_owner_name(activity.create_uid),
                        "action": None,
                    }
                )
        return self._sort_rows_newest_first(rows)

    @api.model
    def get_closed_tasks(self, limit=50):
        if "approval.log" not in self.env:
            return []
        uid = self.env.uid
        since = self._tasks_requests_since_datetime()
        domain = [
            ("user_id", "=", uid),
            ("show_completed_request", "=", True),
            ("creator_uid", "!=", uid),
            ("date", ">=", since),
        ]
        logs = (
            self.env["approval.log"]
            .sudo()
            .search(domain, limit=limit, order="date desc, id desc")
        )
        logs = self._dedupe_approval_logs(logs)
        return self._sort_rows_newest_first(
            self._approval_log_rows(logs, default_status_key="closed")
        )

    @api.model
    def get_pending_requests(self, limit=50):
        if "approval.log" not in self.env:
            return []
        employee = self._get_employee()
        if not employee:
            return []
        since = self._tasks_requests_since_datetime()
        logs = self._approval_logs_for_employee(employee, "pending", since, limit)
        return self._sort_rows_newest_first(
            self._approval_log_rows(logs, default_status_key="pending")
        )

    @api.model
    def get_approved_requests(self, limit=50):
        if "approval.log" not in self.env:
            return []
        employee = self._get_employee()
        if not employee:
            return []
        since = self._tasks_requests_since_datetime()
        logs = self._approval_logs_for_employee(employee, "approved", since, limit)
        return self._sort_rows_newest_first(
            self._approval_log_rows(logs, default_status_key="closed")
        )

    @api.model
    def get_pending_requests_count(self):
        return self.env["mail.activity"].search_count([("user_id", "=", self.env.uid)])

    # ------------------------------------------------------------------ events
    @api.model
    def _event_timeline_status(self, event):
        now = fields.Datetime.now()
        begin = event.date_begin
        end = event.date_end or begin
        if end and end < now:
            return "past"
        if begin and begin <= now and end and end >= now:
            return "ongoing"
        return "upcoming"

    @api.model
    def get_events(self, limit=4, search=None):
        if "event.event" not in self.env:
            return []
        lang = self.env.context.get("lang") or self.env.user.lang or "ar_001"
        domain = []
        if "website_published" in self.env["event.event"]._fields:
            domain.append(("website_published", "=", True))
        query = (search or "").strip()
        if query:
            name_domain = [("name", "ilike", query)]
            if "address_id" in self.env["event.event"]._fields:
                name_domain = expression.OR(
                    [
                        name_domain,
                        [("address_id.name", "ilike", query)],
                        [("address_id.city", "ilike", query)],
                    ]
                )
            if "event_type_id" in self.env["event.event"]._fields:
                name_domain = expression.OR(
                    [name_domain, [("event_type_id.name", "ilike", query)]]
                )
            domain = expression.AND([domain, name_domain]) if domain else name_domain
            limit = max(limit or 0, 50)
        Event = self.env["event.event"].sudo().with_context(lang=lang)
        events = Event.search(domain, order="date_begin desc", limit=limit)
        result = []
        for idx, event in enumerate(events):
            begin = fields.Datetime.context_timestamp(self, event.date_begin)
            day = begin.strftime("%d")
            month = _AR_MONTHS[begin.month - 1]
            meta_parts = []
            if event.event_type_id:
                meta_parts.append(event.event_type_id.name)
            venue = ""
            if event.address_id:
                venue = (
                    event.address_id.name
                    or event.address_id.city
                    or event.address_id.contact_address
                    or ""
                )
            if venue:
                meta_parts.append(venue.strip())
            elif event.organizer_id:
                meta_parts.append(event.organizer_id.name)
            meta = " • ".join(part for part in meta_parts if part)
            url = getattr(event, "website_url", None) or f"/event/{event.id}"
            result.append(
                {
                    "id": event.id,
                    "title": event.name or "",
                    "meta": meta,
                    "day": day,
                    "month": month,
                    "color": _EVENT_COLORS[idx % len(_EVENT_COLORS)],
                    "status": self._event_timeline_status(event),
                    "date_begin": fields.Datetime.to_string(event.date_begin),
                    "date_end": fields.Datetime.to_string(event.date_end),
                    "url": url,
                }
            )
        return result

    @api.model
    def search_portal_sections(self, search="", limit=50):
        """Search news, decisions and events across all published records (not just dashboard preview)."""
        query = (search or "").strip()
        if not query:
            return {
                "news": {"general": [], "press": [], "employees": []},
                "decisions": [],
                "events": [],
            }
        return {
            "news": {
                "general": self.get_news_posts(limit=limit, search=query),
                "press": self.get_press_news(limit=limit, search=query),
                "employees": self.get_employee_news(limit=limit, search=query),
            },
            "decisions": self.get_decisions(limit=limit, search=query),
            "events": self.get_events(limit=limit, search=query),
        }

    # ------------------------------------------------------------------ attendance
    @api.model
    def _act_window_for_xmlid(self, xmlid, **overrides):
        try:
            action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        except ValueError:
            return None
        action.update(overrides)
        return self._serialize_action(action)

    @api.model
    def _approval_new_request_action(self, approval_xmlid, context=None):
        approval = self.env.ref(approval_xmlid, raise_if_not_found=False)
        if not approval:
            return None
        ctx = dict(self.env.context)
        if context:
            ctx.update(context)
        try:
            return self._serialize_action(
                approval.with_context(**ctx).action_new_request()
            )
        except Exception:
            return None

    @api.model
    def _attendance_update_create_action(self, employee, extra_context=None):
        ctx = {
            "default_employee_id": employee.id,
            "default_date": fields.Date.to_string(fields.Date.context_today(self)),
        }
        if extra_context:
            ctx.update(extra_context)
        action = self._approval_new_request_action(
            "attendance_update_record_request.attendance_update_service_approval_model",
            context=ctx,
        )
        if action:
            return action
        if "hr.attendance.summary" not in self.env:
            return None
        return self._serialize_action(
            {
                "type": "ir.actions.act_window",
                "name": "طلب تحديث سجل الحضور",
                "res_model": "hr.attendance.summary",
                "view_mode": "tree",
                "target": "current",
                "context": ctx,
            }
        )

    @api.model
    def get_employee_profile_action(self):
        """Open the current user's hr.employee.public form."""
        employee = self._get_employee()
        if not employee:
            return None
        public_employee = self.env["hr.employee.public"].browse(employee.id)
        if not public_employee.exists():
            return None
        action = {
            "type": "ir.actions.act_window",
            "name": _("My Profile"),
            "res_model": "hr.employee.public",
            "res_id": public_employee.id,
            "view_mode": "form",
            "target": "current",
        }
        form_view = self.env.ref(
            "hr.hr_employee_public_view_form", raise_if_not_found=False
        )
        if form_view:
            action["views"] = [(form_view.id, "form")]
        return self._serialize_action(action)

    @api.model
    def get_help_center_action(self):
        """Open posted FAQs (help center). service_add_faq isn't installed in
        this project — degrade to no action instead of raising, so the
        Help Center button in the navbar can just stay hidden/no-op."""
        try:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "service_add_faq.action_check_post_tree"
            )
        except ValueError:
            return False
        action["target"] = "current"
        return self._serialize_action(action)

    @api.model
    def _attendance_summary_list_action(self, employee):
        """Open the current user's monthly attendance summary tree."""
        if not employee or "hr.attendance.summary" not in self.env:
            return None
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        domain = [
            ("employee_id", "=", employee.id),
            ("date", ">=", month_start),
            ("date", "<=", today),
        ]
        ctx = {"search_default_attendance_by": 1}
        action = self._act_window_for_xmlid(
            "oi_hr_attendance.act_hr_attendance_summary",
            domain=domain,
            context=ctx,
            target="current",
        )
        if action:
            tree_view = self.env.ref(
                "oi_hr_attendance.view_hr_attendance_summary_tree",
                raise_if_not_found=False,
            )
            form_view = self.env.ref(
                "oi_hr_attendance.view_hr_attendance_summary_from",
                raise_if_not_found=False,
            )
            if tree_view:
                views = [(tree_view.id, "tree")]
                if form_view:
                    views.append((form_view.id, "form"))
                action["views"] = views
            return action
        return self._serialize_action(
            {
                "type": "ir.actions.act_window",
                "name": "الحضور والانصراف",
                "res_model": "hr.attendance.summary",
                "view_mode": "tree,form",
                "domain": domain,
                "context": ctx,
                "target": "current",
            }
        )

    @api.model
    def _attendance_card_actions(self, employee):
        actions = {}
        if employee:
            actions["schedule"] = self._attendance_summary_list_action(employee)
        if employee and "hr.leave" in self.env:
            leave_ctx = {
                "default_employee_id": employee.id,
                "form_view_ref": "hr_holidays.hr_leave_view_form",
            }
            absence_action = self._act_window_for_xmlid(
                "hr_holidays.hr_leave_action_my",
                view_mode="form",
                target="current",
                context=leave_ctx,
            )
            if absence_action:
                form_view = self.env.ref(
                    "hr_holidays.hr_leave_view_form",
                    raise_if_not_found=False,
                )
                if form_view:
                    absence_action["views"] = [(form_view.id, "form")]
                actions["absence"] = absence_action
        if employee:
            permission_ctx = {
                "default_permission_leave": True,
                "default_request_unit_hours": True,
                "default_employee_id": employee.id,
            }
            permission_action = self._approval_new_request_action(
                "request_permission_service.request_permission_service_approval_model",
                context=permission_ctx,
            )
            if not permission_action:
                permission_action = self._act_window_for_xmlid(
                    "request_permission_service.ir_actions_act_window_permission_requests",
                    view_mode="form",
                    target="current",
                    context=permission_ctx,
                )
            if permission_action:
                actions["delay"] = permission_action
        if employee:
            actions["no_task"] = self._attendance_update_create_action(
                employee,
                {"default_problem_type": "forget"},
            )
        return actions

    @api.model
    def get_attendance_summary(self, employee=None):
        employee = employee or self._get_employee()
        if not employee or "hr.attendance.summary" not in self.env:
            return {}
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        Summary = self.env["hr.attendance.summary"]
        month_domain = [
            ("employee_id", "=", employee.id),
            ("date", ">=", month_start),
            ("date", "<=", today),
        ]
        month_records = Summary.search(month_domain, order="date desc")
        schedule_count = len(month_records)
        absence_days = len(month_records.filtered(lambda r: r.absent_hours > 0))
        delay_hours = sum(month_records.mapped("late_hours"))
        no_task_count = len(month_records.filtered(lambda r: r.no_check))
        schedule_label = f"{schedule_count} يوم"
        month_name = _AR_MONTHS[today.month - 1]
        schedule_title = f"الحضور والانصراف ({month_name})"
        card_actions = self._attendance_card_actions(employee)
        cards = [
            {
                "key": "schedule",
                "full": True,
                "title": schedule_title,
                "subtitle": schedule_label,
                "action": card_actions.get("schedule"),
            },
            {
                "key": "absence",
                "full": False,
                "title": "الغياب",
                "subtitle": f"{absence_days} يوم",
                "action": card_actions.get("absence"),
            },
            {
                "key": "delay",
                "full": False,
                "title": "التأخير",
                "subtitle": f"{round(delay_hours, 1)} ساعة",
                "action": card_actions.get("delay"),
            },
            {
                "key": "no_task",
                "full": True,
                "title": "عدم وجود بصمة",
                "subtitle": str(no_task_count),
                "action": card_actions.get("no_task"),
            },
        ]
        return {
            "schedule_label": schedule_label,
            "schedule_count": schedule_count,
            "schedule_title": schedule_title,
            "absence_days": absence_days,
            "delay_hours": round(delay_hours, 1),
            "no_task_count": no_task_count,
            "cards": cards,
        }

    # ------------------------------------------------------------------ bootstrap
    @api.model
    def _safe_portal_section(self, default, func):
        """Run a bootstrap loader; never abort the whole dashboard on one failure."""
        try:
            with self.env.cr.savepoint():
                return func()
        except Exception:
            return default

    @api.model
    def get_bootstrap_payload(self):
        employee = self._get_employee()
        profile = self._safe_portal_section({}, lambda: self.get_profile(employee))
        leave_kpis = self._safe_portal_section(
            [], lambda: self.get_leave_kpis(employee)
        )
        pending_count = self._safe_portal_section(
            0, lambda: self.get_pending_requests_count()
        )
        payload = {
            "user_name": profile.get("name") or self.env.user.name,
            "avatar_url": profile.get("avatar_url")
            or f"/web/image/res.partner/{self.env.user.partner_id.id}/avatar_128",
            "department": profile.get("department", ""),
            "job_title": profile.get("job_title", ""),
            "employee_code": profile.get("employee_no", ""),
            "profile": profile,
            "profile_action": self._safe_portal_section(
                None, self.get_employee_profile_action
            ),
            "leave_kpis": leave_kpis,
            "pending_requests_count": pending_count,
            "pending_requests": pending_count,
            "leave_balance_days": 0,
            "news": {
                "general": self._safe_portal_section([], self.get_news_posts),
                "press": self._safe_portal_section([], self.get_press_news),
                "employees": self._safe_portal_section([], self.get_employee_news),
            },
            "decisions": self._safe_portal_section([], self.get_decisions),
            "new_joiners": self._safe_portal_section([], self.get_new_joiners),
            "task_lists": {
                "pending": self._safe_portal_section([], self.get_pending_activities),
                "closed": self._safe_portal_section([], self.get_closed_tasks),
            },
            "request_lists": {
                "pending": self._safe_portal_section([], self.get_pending_requests),
                "closed": self._safe_portal_section([], self.get_approved_requests),
            },
            "events": self._safe_portal_section([], self.get_events),
            "attendance": self._safe_portal_section(
                {}, lambda: self.get_attendance_summary(employee)
            ),
            "quick_links": [],
            "service_categories": self._safe_portal_section(
                [], self.get_service_categories
            ),
        }
        if leave_kpis:
            first_days = next(
                (k for k in leave_kpis if k.get("unit") == "days"), leave_kpis[0]
            )
            try:
                payload["leave_balance_days"] = int(float(first_days.get("value", 0)))
            except (TypeError, ValueError):
                payload["leave_balance_days"] = 0
        Link = self.env["smart.portal.quick.link"]
        links = Link.search([("active", "=", True)], order="sequence, id")
        payload["quick_links"] = [
            {
                "id": link.id,
                "icon": link.icon or "",
                "label": link.name or "",
                "href": link.link_url or "#",
            }
            for link in links
        ]
        return payload

    @api.model
    def _serialize_service_item(self, item):
        action = (
            self._serialize_action(item._get_portal_open_action())
            if item.view_id
            else None
        )
        return {
            "id": item.id,
            "label": item.name or "",
            "href": "#" if action else (item.link_url or "#"),
            "action": action,
        }

    @api.model
    def get_service_categories(self):
        Category = self.env["smart.portal.service.category"]
        categories = Category.search([("active", "=", True)], order="sequence, id")
        result = []
        for category in categories:
            items = []
            for item in category.item_ids.filtered("active").sorted("sequence"):
                try:
                    items.append(self._serialize_service_item(item))
                except Exception:
                    continue
            result.append(
                {
                    "id": category.id,
                    "key": category.code or "",
                    "label": category.name or "",
                    "items": items,
                }
            )
        return result
