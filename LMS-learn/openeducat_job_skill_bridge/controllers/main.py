# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class StudentSkillPortal(CustomerPortal):

    def _get_current_student(self):
        return request.env["op.student"].sudo().search(
            [("partner_id", "=", request.env.user.partner_id.id)],
            limit=1,
        )

    @http.route(
        ["/student/skill", "/student/skill/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def enterprise_portal_student_skill(self, page=1, **kwargs):
        student = self._get_current_student()
        if not student:
            return request.not_found()

        skills = request.env["op.student.skill.name"].sudo().search([
            ("self_assessed", "=", True),
            "|",
            ("company_id", "=", False),
            ("company_id", "in", request.env.companies.ids),
        ])
        levels = request.env["op.student.skill.level.name"].sudo().search(
            [],
            order="progress, name",
        )

        return request.render(
            "openeducat_job_skill_bridge.enterprise_add_student_skill_portal",
            {
                "skill_ids": skills,
                "level_ids": levels,
                "student": student,
                "user": student,
                "page_name": "student_skill_form",
            },
        )

    @http.route(
        ["/student/skill/submit"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def enterprise_portal_add_student_skill(
        self,
        skill_type_id=None,
        level_id=None,
        **kwargs,
    ):
        student = self._get_current_student()
        if not student:
            return request.not_found()

        try:
            skill_id = int(skill_type_id)
            level_record_id = int(level_id)
        except (TypeError, ValueError):
            return request.redirect("/student/skill")

        skill = request.env["op.student.skill.name"].sudo().browse(
            skill_id
        ).exists()
        level = request.env["op.student.skill.level.name"].sudo().browse(
            level_record_id
        ).exists()

        if not skill or not level or not skill.self_assessed:
            return request.redirect("/student/skill")

        existing = request.env["op.skill.line"].sudo().search([
            ("student_id", "=", student.id),
            ("skill_type_id", "=", skill.id),
        ], limit=1)

        values = {
            "student_id": student.id,
            "skill_type_id": skill.id,
            "level_id": level.id,
            "company_id": student.company_id.id or request.env.company.id,
        }
        if existing:
            existing.write({"level_id": level.id})
        else:
            request.env["op.skill.line"].sudo().create(values)

        return request.redirect("/student/profile")
