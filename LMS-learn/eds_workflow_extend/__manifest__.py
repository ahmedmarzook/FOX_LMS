# -*- coding: utf-8 -*-
{
    "name": "Workflow Engine Extend",
    "summary": "Workflow Engine Extend with Workflow Department Support",
    "version": "19.0.1.7.0",
    "category": "Extra Tools",
    "website": "https://www.edraksys.com",
    "description": """
Workflow Engine Extend
======================

This module extends the workflow engine with additional features:

**Workflow Department Separation**
- Adds workflow_department_id field to hr.employee
- Separates budget allocation (department_id) from approval routing (workflow_department_id)
- All approval workflows use workflow_department_id if set, otherwise fall back to department_id
- Budget calculations continue to use department_id unchanged

**Use Case:**
When an employee's budget is allocated to Department A, but their approvals 
should follow Department B's hierarchy, set:
- department_id = Department A (for budget)
- workflow_department_id = Department B (for approvals)

**Filter Condition Usage:**
Use get_workflow_department() method in filter conditions:
- record.employee_id.get_workflow_department().manager_id.user_id == user
- record.employee_id.get_workflow_department().vp_id.user_id == user
""",
    "depends": [
        "eds_workflow",
        "hr",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/view.xml",
        "views/hr_employee_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
