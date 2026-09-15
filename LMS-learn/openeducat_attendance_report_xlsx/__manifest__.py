# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

{
    "name": "OpenEduCat Attendance Report XLSX",
    "summary": "Base XLSX reporting support used by OpenEduCat attendance reports.",
    "author": "OpenEduCat Inc",
    "website": "https://www.openeducat.org",
    "category": "Education",
    "version": "19.0.1.0.0",
    "license": "Other proprietary",
    "external_dependencies": {
        "python": ["xlsxwriter"],
    },
    "depends": ["base", "web"],
    "data": [
        "menu/report.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "openeducat_attendance_report_xlsx/static/src/js/report/action_manager_report.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
