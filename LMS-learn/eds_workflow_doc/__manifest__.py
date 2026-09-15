# -*- coding: utf-8 -*-
# Copyright 2018 Openinside co. W.L.L.
{
    "name": "Custom Document Model",
    "summary": "Custom Workflow Model, Form Builder, Shared Services, General Services, Custom Forms, Customized Forms, Form Generator, Ad-hoc Forms",
    "version": "19.0.1.2.3",
    "category": "Extra Tools",
    "website": "https://www.edraksys.com",
    "description": """
		Custom Document Model
		 
    """,
    "images": ["static/description/cover.png"],
    "author": "EdrakSys",
    "license": "OPL-1",
    "price": 100,
    "currency": "USD",
    "installable": True,
    "depends": ["eds_workflow", "hr"],
    "data": [
        "view/approval_model.xml",
        "view/approval_model_kanban.xml",
        "view/approval_model_excel.xml",
        "view/approval_doc.xml",
        "view/show_as_service.xml",
        "view/action.xml",
        "view/menu.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "eds_workflow_doc/static/src/fields/many2many_as_one2many.js"
        ]
    },
    "odoo-apps": True,
}
