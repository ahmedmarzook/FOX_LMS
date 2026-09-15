# -*- coding: utf-8 -*-
{
    "name": "Delegation",
    "version": "19.0.1.0.0",
    "author": "EdrakSys",
    "license": "OPL-1",
    "price": 999.99,
    "currency": "EUR",
    "sequence": 100,
    "category": "Human Resources",
    "website": "https://www.edraksys.com",
    "summary": "Delegation, Approval, Access Right, Temprorary Access, Role Delegation, Assign, Assign Rights, Assign Roles",
    "description": """ Allow Employee to delegate his roles to another employee
""",
    "depends": ["base", "hr", "mail", "eds_base"],
    "data": [
        "data/ir_cron.xml",
        "data/mail_template.xml",
        "data/sequences.xml",
        "security/group.xml",
        "security/ir.model.access.csv",
        "security/rules.xml",
        "view/delegation.xml",
        "view/mail_template.xml",
        "view/res_groups.xml",
        "view/action.xml",
        "view/menu.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False
}
