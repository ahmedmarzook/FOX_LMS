# -*- coding: utf-8 -*-
{
    "name": "Login as another user",
    "summary": "Login as/impersonate another user, Login As, Other Users, Admin Users, "
    "Administrator, Super User, Portal User, Portal Hijack",
    "version": "19.0.1.0.0",
    "category": "Extra Tools",
    "website": "https://www.edraksys.com",
    "description": """
"""
    """		 * allow administrator to login as/impersonate normal user
"""
    """		 * allow administrator to login as/impersonate portal user
"""
    """		 * login back to administrator
"""
    """		 
"""
    "    ",
    "images": ["static/description/cover.png"],
    "author": "EdrakSys",
    "license": "OPL-1",
    "price": 30.0,
    "currency": "EUR",
    "installable": True,
    "depends": ["web"],
    "data": ["security/ir.model.access.csv", "view/action.xml", "view/login_as.xml"],
    "assets": {
        "web.assets_backend": [
            "eds_login_as/static/src/css/login_as.css",
            "eds_login_as/static/src/xml/templates.xml",
            "eds_login_as/static/src/js/login_as.js",
        ],
    },
    "external_dependencies": {},
    "auto_install": False,
    "odoo-apps": True,
    "application": False,
}
