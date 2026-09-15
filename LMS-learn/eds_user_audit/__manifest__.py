# -*- coding: utf-8 -*-

{
    "name": "User Activity Audit",
    "summary": """
            User Log, Log Report, Record Log, Record Info, Record Information, User Activity, Record History, Log History
        """,
    "description": """
        User Activity Audit
    """,
    "category": "Extra Tools",
    "version": "19.0.1.1.17",
    "author": "EdrakSys",
    "website": "https://www.edraksys.com",
    "license": "OPL-1",
    "price": 99.99,
    "currency": "EUR",
    # any module necessary for this one to work correctly
    "depends": ["base", "mail", "web"],
    # always loaded
    "data": [
        "security/group.xml",
        "security/ir.model.access.csv",
        "views/audit_log.xml",
        "views/audit_config.xml",
        "views/mail_tracking_value.xml",
        "views/audit_log_detail.xml",
        "views/audit_delete.xml",
        "views/action.xml",
        "views/menu.xml",
        "data/audit_type.xml",
    ],
    # 'qweb' : [
    #         "static/src/xml/*.xml",
    #     ],
    # 'images':[
    #     'static/description/cover.png'
    # ],
    # 'assets': {
    #         'web.assets_backend': [
    #             'eds_user_audit/static/src/js/sidebar.js',
    #             "eds_user_audit/static/src/xml/*.xml",
    #         ],
    #     },
    "installable": True,
    "odoo-apps": True,
    "auto_install": False,
}
