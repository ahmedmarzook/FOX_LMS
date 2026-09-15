# -*- coding: utf-8 -*-
# Copyright 2018 Openinside co. W.L.L.
{
    "name": "Advance activity menu",
    "summary": "Advance activity menu",
    "version": "19.0.1.1.11",
    "category": "Extra Tools",
    "website": "https://www.edraksys.com",
    "description": """
		Separate model activities by record type
		set window action for activity
		set icon for activity
		set title for activity
    """,
    "images": ["static/description/cover.png"],
    "author": "EdrakSys",
    "license": "OPL-1",
    "price": 70,
    "currency": "EUR",
    "depends": ["eds_mail"],
    "data": [
        "views/mail_activity_menu.xml",
        "views/action.xml",
        "views/menu.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "odoo-apps": False,
    "auto_install": False,
}
