{
    "name": "Base Extension",
    "summary": "Utilities functions for base model",
    "author": "EdrakSys",
    "license": "OPL-1",
    "version": "19.0.1.0",
    "depends": ["base", "web"],
    "data": [
        "view/ir_module_module.xml",
        "view/ir_rule.xml",
        "view/ir_ui_menu.xml",
        "view/ir_actions_server.xml",
        "view/ir_ui_view.xml",
        "view/ir_model_fields.xml",
        "view/ir_default.xml",
        "view/action.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "eds_base/static/src/js/*.js",
            "eds_base/static/src/xml/*.xml",
        ]
    },
    "installable": True,
    "auto_install": False,
    "application": False
}