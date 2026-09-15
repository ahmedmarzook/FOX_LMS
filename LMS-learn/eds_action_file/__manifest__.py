# -*- coding: utf-8 -*-
# Copyright 2018 Openinside co. W.L.L.
{
    "name": "Client Action File Download",
    "summary": "Client Action File Download",
    "version": "19.0.1.1.1",
    "category": "Extra Tools",
    "website": "https://www.edraksys.com",
    "description": """
		Client Action File Download 
		 
    """,
    "images": ["static/description/cover.png"],
    "author": "EdrakSys",
    "license": "OPL-1",
    "price": 9,
    "currency": "USD",
    "installable": True,
    "depends": ["web"],
    "data": [],
    "auto_install": False,
    "odoo-apps": True,
    "assets": {
        "web.assets_backend": ["eds_action_file/static/src/js/action_file_download.js"]
    },
}
