{
    "name": "OpenEduCat Live Attendance",
    "summary": "Manage student attendance during OpenEduCat live meetings",
    "version": "19.0.1.0",
    "category": "Productivity/Discuss",
    "sequence": 145,
    "author": "OpenEduCat Inc",
    "company": "OpenEduCat Inc.",
    "website": "https://www.openeducat.org",
    "depends": [
        "mail",
        "openeducat_attendance",
        "openeducat_live",
    ],
    "data": [
        "views/calendar_event.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "openeducat_live_attendance/static/src/js/live_attendance_systray.js",
            "openeducat_live_attendance/static/src/xml/live_attendance_systray.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "Other proprietary",
}
