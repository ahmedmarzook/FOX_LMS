{
    "name": "OpenEduCat Live Assignment",
    "summary": "Create assignments directly from OpenEduCat live meetings",
    "version": "19.0.1.0",
    "category": "Productivity/Discuss",
    "sequence": 145,
    "author": "OpenEduCat Inc",
    "company": "OpenEduCat Inc.",
    "website": "https://www.openeducat.org",
    "depends": [
        "mail",
        "openeducat_assignment_enterprise",
        "openeducat_live",
    ],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "openeducat_live_assignment/static/src/js/live_assignment_systray.js",
            "openeducat_live_assignment/static/src/xml/live_assignment_systray.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "Other proprietary",
}
