# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

{
    'name': 'Openeducat Lesson Enterprise',
    'summary': 'This module allows you to manage the lesson planning.\n    This module adds feature to manage the session to OpenEduCat.',
    'version': '19.0.1.0.1',
    'category': 'Education',
    'sequence': 1,
    'complexity': 'easy',
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_timetable',
        'openeducat_parent',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/op_lesson_security.xml',
        'data/ir_sequence.xml',
        'views/lesson_view.xml',
        'menus/openeducat_lesson_menu.xml',
        'report/lesson_menu.xml',
        'report/report_lesson_planning.xml',
    ],
    'demo': [
        'demo/op_lesson_demo.xml',
    ],
    'images': [
        'static/description/openeducat_lesson_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans',
}
