from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    workflow_department_id = fields.Many2one(
        "hr.department",
        string="الوحدة الادارية",
        help="Department used for approval workflows and routing. "
        "If not set, falls back to the main department. "
        "Use this to separate budget allocation (department_id) from approval routing.",
        tracking=True,
        company_dependent=False,
    )

    @api.depends("department_id", "workflow_department_id")
    def _compute_effective_workflow_department(self):
        """Compute the effective department to use for workflow routing"""
        for emp in self:
            emp.effective_workflow_department_id = (
                emp.workflow_department_id or emp.department_id
            )

    effective_workflow_department_id = fields.Many2one(
        "hr.department",
        string="Effective Workflow Department",
        compute="_compute_effective_workflow_department",
        store=True,
        help="The department actually used for workflow routing. "
        "This is workflow_department_id if set, otherwise department_id.",
    )

    def get_workflow_department(self):
        """
        Get the department used for workflow routing.
        This method can be used in approval filter conditions.

        Returns:
            hr.department: The workflow department (workflow_department_id if set,
                          otherwise department_id)

        Usage in filter_condition:
            record.employee_id.get_workflow_department().manager_id.user_id == user
            record.employee_id.get_workflow_department().vp_id.user_id == user
            record.employee_id.get_workflow_department().general_manager.user_id == user
        """
        self.ensure_one()
        return self.workflow_department_id or self.department_id
