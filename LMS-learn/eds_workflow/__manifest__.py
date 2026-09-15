# -*- coding: utf-8 -*-
{
    "name": "Workflow Engine Base",
    "summary": "Configurable Workflow Engine, Workflow, Workflow Engine, Approval, Approval "
    "Engine, Approval Process, Escalation, Multi Level Approval",
    "version": "19.0.1.6.8",
    "category": "Extra Tools",
    "website": "https://www.edraksys.com",
    "description": """
    		Configurable Workflow Engine
    		 
        """,
    "images": ["static/description/cover.png"],
    "author": "EdrakSys",
    "license": "OPL-1",
    "price": 400.0,
    "currency": "USD",
    "installable": True,
    "depends": [
        "mail",
        "eds_base",
        "web",
        "base_automation",
        "eds_fields_selection",
        "eds_web_selection_field_dynamic",
    ],
    "data": [
        "data/ir_sequence.xml",
        "view/approval_config.xml",
        "view/approval_approve_wizard.xml",
        "view/approval_reject_wizard.xml",
        "view/approval_forward_wizard.xml",
        "view/approval_return_wizard.xml",
        "view/approval_transfer_wizard.xml",
        "view/approval_cancel_wizard.xml",
        "view/approval_escalation.xml",
        "view/approval_state_update.xml",
        "view/approval_settings.xml",
        "view/cancellation_record_view.xml",
        # NOTE: approval_superuser_intervention_report moved to mawhiba_bot_intervention_report module
        "security/ir.model.access.csv",
        "view/action.xml",
        "view/menu.xml",
        "view/templates.xml",
        "data/mail_activity_type.xml",
        "view/res_config_settings.xml",
        "data/ir_cron.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "eds_workflow/static/src/js/*.js",
            "eds_workflow/static/src/xml/*.xml",
        ]
    },
    "odoo-apps": True,
    "application": False,
}
