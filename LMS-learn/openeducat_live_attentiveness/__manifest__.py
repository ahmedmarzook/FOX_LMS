{
    "name": "OpenEduCat Live Attentiveness",
    "summary": "Track participant attentiveness during OpenEduCat live meetings",
    "version": "19.0.1.0",
    "category": "Productivity/Discuss",
    "sequence": 145,
    "author": "OpenEduCat Inc",
    "company": "OpenEduCat Inc.",
    "website": "https://www.openeducat.org",
    "depends": [
        "mail",
        "calendar",
        "openeducat_live",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/calendar_event.xml",
        "views/op_logs_attentive_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "openeducat_live_attentiveness/static/src/js/attentiveness_service.js",
            "openeducat_live_attentiveness/static/src/js/rtc_session.js",
            "openeducat_live_attentiveness/static/src/js/rtc_controller.js",
            "openeducat_live_attentiveness/static/src/xml/attentiveness_systray.xml",
        ],
        "mail.assets_discuss_public": [
            "openeducat_live_attentiveness/static/src/js/attentiveness_service.js",
            "openeducat_live_attentiveness/static/src/js/rtc_session.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "Other proprietary",
}
