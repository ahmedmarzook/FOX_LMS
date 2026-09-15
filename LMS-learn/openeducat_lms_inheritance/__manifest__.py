# -*- coding: utf-8 -*-
{
    'name': 'OpenEduCat LMS Inheritance',
    'version': '1.0',
    'summary': 'Adds a Doctor Name field and a Course Files attachment '
               '(files, images, URLs) to Online Courses.',
    'category': 'Education',
    'depends': ['openeducat_lms'],
    'data': [
        'security/ir.model.access.csv',
        'views/op_course_views.xml',
        'wizard/op_course_attach_url_wizard_views.xml',
    ],
'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
