{
    'name': 'OpenEduCat Activity',
    'version': '19.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    'sequence': 3,
    'summary': 'Manage Activities',
    'author': 'OpenEduCat Inc',
    'website': 'https://www.openeducat.org',
    'depends': [
        'openeducat_core',
    ],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'data/activity_type_data.xml',
        'wizard/student_migrate_wizard_view.xml',
        'views/activity_view.xml',
        'views/activity_type_view.xml',
        'views/student_view.xml',
        'menus/op_menu.xml',
    ],
    'demo': [
        'demo/activity_demo.xml',
    ],
    'images': [
        'static/description/openeducat_activity_banner.jpg',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
