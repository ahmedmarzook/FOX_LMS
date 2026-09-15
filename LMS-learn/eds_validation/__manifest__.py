# -*- coding: utf-8 -*-

{
    "name": "Business Rules",
    "summary": "Configurable validation in any object, Validation, Policy, Rules, Conditions, Statute",
    "category": "Extra Tools",
    "website": "https://www.edraksys.com",
    "author": "EdrakSys",
    "version": "19.0.0.1",
    "license": "AGPL-3",
    "price": 199.9,
    "currency": "EUR",
    "installable": True,
    "depends": ["base", "mail", "web", "bus"],
    "data": [
        "security/ir.model.access.csv",
        "view/validation.xml",
        "view/validation_group.xml",
        "view/validation_log.xml",
        "view/action.xml",
        "view/menu.xml",
    ],
    "assets": {"web.assets_backend": ["eds_validation/static/src/xml/templates.xml"]},
    "application": False,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "odoo-apps": True,
    "images": ["static/description/cover.png"],
}
