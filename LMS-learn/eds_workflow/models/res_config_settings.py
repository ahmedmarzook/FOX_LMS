"""
Created on Jun 28, 2020

@author: Zuhair Hammadi
"""

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_eds_workflow_expense = fields.Boolean(string="Employee Expenses")
    module_eds_workflow_hr_contract = fields.Boolean(string="Employee Contracts")
    module_eds_workflow_hr_holidays = fields.Boolean(string="Employee Time Off")
    module_eds_workflow_hr_holidays_manager = fields.Boolean(
        string="Employee Time Off / Employee Manager"
    )
    module_eds_workflow_hr_payslip_run = fields.Boolean(
        string="Payslip Batches (Community)"
    )
    module_eds_workflow_hr_payslip_run_e = fields.Boolean(
        string="Payslip Batches (Enterprise)"
    )
    module_eds_workflow_purchase_order = fields.Boolean(string="Purchase Order")
    module_eds_workflow_purchase_requisition = fields.Boolean()
    module_eds_workflow_sale_order = fields.Boolean(string="Sale Order")

    module_eds_workflow_doc = fields.Boolean(string="Manual Model")

    @api.onchange(
        "module_eds_workflow_expense",
        "module_eds_workflow_hr_contract",
        "module_eds_workflow_hr_holidays",
        "module_eds_workflow_hr_holidays_manager",
        "module_eds_workflow_hr_payslip_run",
        "module_eds_workflow_purchase_requisition",
        "module_eds_workflow_sale_order",
        "module_eds_workflow_doc",
    )
    def _onchange_workflow(self):
        for name in (
            "module_eds_workflow_expense",
            "module_eds_workflow_hr_contract",
            "module_eds_workflow_hr_holidays",
            "module_eds_workflow_hr_holidays_manager",
            "module_eds_workflow_hr_payslip_run",
            "module_eds_workflow_purchase_requisition",
            "module_eds_workflow_sale_order",
            "module_eds_workflow_doc",
        ):
            module_name = name[7:]
            if self[name]:
                if not self.env["ir.module.module"].get_module_info(module_name):
                    self[name] = False
                    return {
                        "warning": {
                            "title": "Module not found",
                            "message": """Module (%s) is not available in your system
Please download it from                            
https://apps.odoo.com/apps/17.0/%s/"""
                            % (module_name, module_name),
                        }
                    }
