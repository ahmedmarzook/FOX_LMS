{
    "name": "OpenEduCat Live",
    "summary": "Live educational meetings integrated with Calendar and Discuss",
    "version": "19.0.1.0",
    "category": "Productivity/Discuss",
    "sequence": 145,
    "author": "OpenEduCat Inc",
    "company": "OpenEduCat Inc.",
    "website": "https://www.openeducat.org",
    "depends": [
        "base",
        "mail",
        "calendar",
        "openeducat_core_enterprise",
        "openeducat_meeting_enterprise",
        "openeducat_online_tools_enterprise",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/calendar_event.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "openeducat_live/static/src/js/live_service.js",
            "openeducat_live/static/src/create_meet_calendar/create_meet_calendar.js",
            "openeducat_live/static/src/xml/create_meet_calendar.xml",
            "openeducat_live/static/src/css/style.css",
            "openeducat_live/static/src/scss/style.scss",
        ],
        "mail.assets_discuss_public": [
            "openeducat_live/static/src/js/live_service.js",
            "openeducat_live/static/src/css/style.css",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "Other proprietary",
}
