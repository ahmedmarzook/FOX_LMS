from collections import OrderedDict
from operator import itemgetter

from markupsafe import Markup

from odoo import _, fields, http
from odoo.http import request
from odoo.osv import expression
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL


PPG = 10


class AlumniJobPost(CustomerPortal):

    def _current_student(self):
        return request.env["op.student"].sudo().search(
            [
                "|",
                ("user_id", "=", request.env.user.id),
                ("partner_id", "=", request.env.user.partner_id.id),
            ],
            limit=1,
        )

    def _is_current_alumni(self):
        student = self._current_student()
        return student and student.alumni_boolean

    def _owned_job(self, job_id):
        student = self._current_student()
        if not student:
            return request.env["op.job.post"]
        return request.env["op.job.post"].sudo().search(
            [
                ("id", "=", job_id),
                ("created_by", "=", "alumni"),
                ("alumni_student_id", "=", student.id),
            ],
            limit=1,
        )

    def _selection_data(self):
        return {
            "emp_type": request.env["op.job.type"].sudo().search([]),
            "skill_obj": request.env["op.student.skill.name"].sudo().search([]),
            "country_obj": request.env["res.country"].sudo().search([]),
            "state_obj": request.env["res.country.state"].sudo().search([]),
        }

    def _job_values_from_post(self, post):
        def integer(name, default=False):
            value = post.get(name)
            try:
                return int(value) if value not in (None, "", False) else default
            except (TypeError, ValueError):
                return default

        skill_ids = []
        for value in request.httprequest.form.getlist("skill_ids"):
            try:
                skill_ids.append(int(value))
            except (TypeError, ValueError):
                continue

        start_date = fields.Date.to_date(post.get("start_date"))
        end_date = fields.Date.to_date(post.get("end_date"))

        return {
            "job_post": (post.get("job_post") or "").strip(),
            "salary_from": float(post.get("salary_from") or 0.0),
            "salary_upto": float(post.get("salary_upto") or 0.0),
            "street": (post.get("street") or "").strip(),
            "street2": (post.get("street2") or "").strip(),
            "city": (post.get("city") or "").strip(),
            "zip": (post.get("zip") or "").strip(),
            "country_id": integer("country_id"),
            "state_id": integer("state_id"),
            "start_date": start_date,
            "end_date": end_date,
            "created_by": "alumni",
            "payable_at": post.get("payable_at") or False,
            "expected_employees": integer("expected_employees", 0),
            "description": (post.get("description") or "").strip(),
            "employment_type": integer("employment_type"),
            "skill_ids": [(6, 0, skill_ids)],
        }

    @http.route(
        ["/alumni/job", "/alumni/job/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_alumni_job_post(self, page=1, **kwargs):
        if not self._is_current_alumni():
            return request.not_found()
        values = self._selection_data()
        values.update({"page_name": "alumni_job_form"})
        return request.render(
            "openeducat_alumni_job_enterprise.portal_student_alumni_job",
            values,
        )

    @http.route(
        ["/alumni/job/submit"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def portal_alumni_job_post_submit(self, **post):
        student = self._current_student()
        if not student or not student.alumni_boolean:
            return request.not_found()

        values = self._job_values_from_post(post)
        values["alumni_student_id"] = student.id
        request.env["op.job.post"].sudo().create(values)
        return request.redirect("/alumni/job/list")

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        values["alumni_count"] = request.env["op.job.post"].sudo().search_count(
            [("created_by", "=", "alumni")]
        )
        return values

    def _search_domain(self, search, search_in):
        if not search:
            return []
        fields_map = {
            "sequence": "name",
            "created_by": "created_by",
            "salary_from": "salary_from",
            "salary_upto": "salary_upto",
            "start_date": "start_date",
            "end_date": "end_date",
            "job_post": "job_post",
            "payable_at": "payable_at",
        }
        if search_in == "all":
            return expression.OR([
                [(field_name, "ilike", search)]
                for field_name in fields_map.values()
            ])
        field_name = fields_map.get(search_in, "name")
        return [(field_name, "ilike", search)]

    @http.route(
        [
            "/alumni/job/list",
            "/alumni/job/list/<int:student_id>",
            "/alumni/job/list/page/<int:page>",
            "/alumni/job/list/<int:student_id>/page/<int:page>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def portal_alumni_job_post_list(
        self,
        student_id=None,
        date_begin=None,
        date_end=None,
        page=1,
        sortby=None,
        filterby=None,
        search="",
        search_in="sequence",
        groupby="created_by",
        **post,
    ):
        values = self._prepare_portal_layout_values()
        current_student = self._current_student()
        is_alumni = bool(current_student and current_student.alumni_boolean)

        searchbar_sortings = {
            "name": {"label": _("Name"), "order": "name"},
            "payable_at": {"label": _("Payable At"), "order": "payable_at"},
            "end_date": {"label": _("End Date"), "order": "end_date desc"},
            "start_date": {"label": _("Start Date"), "order": "start_date"},
            "states": {"label": _("Status"), "order": "states"},
        }
        searchbar_filters = {
            "all": {"label": _("All"), "domain": []},
            "created_by_alumni": {
                "label": _("Created By Alumni"),
                "domain": [("created_by", "=", "alumni")],
            },
            "created_by_placement": {
                "label": _("Created By Placement"),
                "domain": [("created_by", "=", "placement")],
            },
            "payable_at_monthly": {
                "label": _("Payable At Monthly"),
                "domain": [("payable_at", "=", "monthly")],
            },
            "payable_at_weekly": {
                "label": _("Payable At Weekly"),
                "domain": [("payable_at", "=", "weekly")],
            },
            "payable_at_yearly": {
                "label": _("Payable At Yearly"),
                "domain": [("payable_at", "=", "yearly")],
            },
        }
        searchbar_inputs = {
            "sequence": {
                "input": "sequence",
                "label": Markup(_("Search<span class='nolabel'> (in name)</span>")),
            },
            "created_by": {"input": "created_by", "label": _("Search in Created By")},
            "salary_from": {"input": "salary_from", "label": _("Search in Salary From")},
            "salary_upto": {"input": "salary_upto", "label": _("Search in Salary Upto")},
            "start_date": {"input": "start_date", "label": _("Search in Start Date")},
            "end_date": {"input": "end_date", "label": _("Search in End Date")},
            "job_post": {"input": "job_post", "label": _("Search in Job Post")},
            "payable_at": {"input": "payable_at", "label": _("Search in Payable At")},
            "all": {"input": "all", "label": _("Search in All")},
        }
        searchbar_groupby = {
            "none": {"input": "none", "label": _("None")},
            "created_by": {"input": "created_by", "label": _("Created By")},
        }

        sortby = sortby if sortby in searchbar_sortings else "name"
        filterby = filterby if filterby in searchbar_filters else "all"
        groupby = groupby if groupby in searchbar_groupby else "created_by"

        domain = list(searchbar_filters[filterby]["domain"])
        domain += self._search_domain(search, search_in)

        total = request.env["op.job.post"].sudo().search_count(domain)
        base_url = (
            f"/alumni/job/list/{student_id}"
            if student_id
            else "/alumni/job/list"
        )
        pager = portal_pager(
            url=base_url,
            url_args={
                "sortby": sortby,
                "filterby": filterby,
                "search": search,
                "search_in": search_in,
                "groupby": groupby,
            },
            total=total,
            page=page,
            step=PPG,
        )

        order = searchbar_sortings[sortby]["order"]
        if groupby == "created_by":
            order = f"created_by, {order}"

        jobs = request.env["op.job.post"].sudo().search(
            domain,
            order=order,
            limit=PPG,
            offset=pager["offset"],
        )

        if is_alumni:
            own_jobs = jobs.filtered(
                lambda job: job.alumni_student_id == current_student
            )
            other_jobs = jobs - own_jobs
            grouped_own = (
                [
                    request.env["op.job.post"].sudo().concat(*records)
                    for _, records in groupbyelem(
                        own_jobs, itemgetter("created_by")
                    )
                ]
                if groupby == "created_by"
                else [own_jobs]
            )
            grouped_other = (
                [
                    request.env["op.job.post"].sudo().concat(*records)
                    for _, records in groupbyelem(
                        other_jobs, itemgetter("created_by")
                    )
                ]
                if groupby == "created_by"
                else [other_jobs]
            )
        else:
            grouped_own = []
            grouped_other = (
                [
                    request.env["op.job.post"].sudo().concat(*records)
                    for _, records in groupbyelem(
                        jobs, itemgetter("created_by")
                    )
                ]
                if groupby == "created_by"
                else [jobs]
            )

        values.update({
            "date": date_begin,
            "alumni": jobs,
            "alumni_student": is_alumni,
            "alumni_others": jobs,
            "page_name": "Alumni_List",
            "pager": pager,
            "ppg": PPG,
            "keep": QueryURL(
                base_url,
                search=search,
                sortby=sortby,
                filterby=filterby,
                search_in=search_in,
                groupby=groupby,
            ),
            "stud_id": student_id,
            "searchbar_filters": OrderedDict(searchbar_filters.items()),
            "filterby": filterby,
            "default_url": base_url,
            "searchbar_sortings": searchbar_sortings,
            "sortby": sortby,
            "attrib_values": [],
            "attrib_set": set(),
            "searchbar_inputs": searchbar_inputs,
            "search_in": search_in,
            "grouped_tasks": grouped_other,
            "grouped_tasks_student": grouped_own,
            "searchbar_groupby": searchbar_groupby,
            "groupby": groupby,
        })

        template = (
            "openeducat_alumni_job_enterprise.Alumni_posted_job_list"
            if is_alumni and not student_id
            else "openeducat_alumni_job_enterprise.portal_student_alumni_job_list"
        )
        return request.render(template, values)

    @http.route(
        [
            "/alumni/job/details/<int:alumni_id>",
            "/alumni/job/details/<int:student_id>/<int:alumni_id>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def portal_alumni_job_post_list_details(
        self, alumni_id, student_id=None, **kwargs
    ):
        job = request.env["op.job.post"].sudo().browse(alumni_id).exists()
        if not job:
            return request.not_found()
        return request.render(
            "openeducat_alumni_job_enterprise.porta_alumni_list_details",
            {
                "alumni_data": job,
                "student": student_id,
                "page_name": "alumni_job_info",
            },
        )

    @http.route(
        ["/alumni/job/delete/<int:alumni>"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def delete_alumni(self, alumni, **post):
        job = self._owned_job(alumni)
        if not job:
            return request.not_found()
        job.unlink()
        return request.redirect("/alumni/job/list")

    @http.route(
        ["/alumni/job/data/<int:alumni_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_alumni_job_post_list_data(self, alumni_id, **kwargs):
        job = self._owned_job(alumni_id)
        if not job:
            return request.not_found()
        values = self._selection_data()
        values.update({
            "alumni_data": job,
            "page_name": "alumni_job_edit",
        })
        return request.render(
            "openeducat_alumni_job_enterprise.portal_alumni_job_list_data",
            values,
        )

    @http.route(
        ["/alumni/job/update/<int:alumni_id>"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def portal_alumni_job_post_data_edit(self, alumni_id, **post):
        job = self._owned_job(alumni_id)
        if not job:
            return request.not_found()
        job.write(self._job_values_from_post(post))
        return request.redirect("/alumni/job/list")

    @http.route(
        ["/get/country_data"],
        type="jsonrpc",
        auth="user",
        website=True,
    )
    def get_country_data(self, country_id=None, **kwargs):
        try:
            country_id = int(country_id)
        except (TypeError, ValueError):
            return {"state_list": []}
        states = request.env["res.country.state"].sudo().search(
            [("country_id", "=", country_id)],
            order="name",
        )
        return {
            "state_list": [
                {"id": state.id, "name": state.name}
                for state in states
            ]
        }
