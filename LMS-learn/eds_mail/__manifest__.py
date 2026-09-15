# -*- coding: utf-8 -*-
# Copyright 2018 Openinside co. W.L.L.
{
    "name": "Discuss Extension",
    "summary": "Discuss Extension",
    "version": "19.0.1.0.0",
    "category": "Extra Tools",
    "website": "https://www.edraksys.com",
    "description": """
		Discuss Extension 
		* add field [Partners with Need Action] in mail template
    """,
    "images": ["static/description/cover.png"],
    "author": "EdrakSys",
    "license": "OPL-1",
    "price": 9.99,
    "currency": "EUR",
    "depends": ["mail"],
    "data": [
        "view/mail_template.xml",
        "view/email_template_preview.xml",
        "view/web_assets.xml",
    ],
    "installable": True,
    "odoo-apps": True,
    "auto_install": False,
}
