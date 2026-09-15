# -*- coding: utf-8 -*-
# Copyright 2018 Openinside co. W.L.L.
{
    "name": "Client Action Message",
    "summary": "Client Action Message, Send Pop-up Messages to Users, Sending a Message or Notification to The User, Alert or Notification Message in The Form of a Pop-Up Message on Clients",
    "version": "19.0.1.1.2",
    "category": "Extra Tools",
    "website": "https://www.edraksys.com",
    "description": """
		Client Action Message

    """,
    "images": ["static/description/cover.png"],
    "author": "EdrakSys",
    "license": "OPL-1",
    "price": 9.99,
    "currency": "EUR",
    "installable": True,
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "eds_action_message/static/src/js/action_manager.js",
        ],
    },
    "data": [],
    "auto_install": False,
    "odoo-apps": True,
}
