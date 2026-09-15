# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

{
    'name': 'OpenEduCat LMS Admission',
    'summary': 'Manage the admission process for LMS courses.',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'sequence': 3,
    'author': 'OpenEduCat Inc',
    'website': 'https://www.openeducat.org',
    'depends': [
        'openeducat_lms',
        'openeducat_admission_enterprise',
    ],
    'data': [
        'views/course_view.xml',
    ],
'images': [
        '',
    ],
    'license': 'Other proprietary',
    'installable': True,
    'application': False,
    'auto_install': False,
}
