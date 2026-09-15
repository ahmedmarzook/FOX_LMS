# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
{
    'name': 'OpenEduCat LMS Forum',
    'summary': 'Integrates course forums with OpenEduCat LMS.',
    'version': '19.0.1.0.1',
    'category': 'Education',
    'sequence': 3,
    'author': 'OpenEduCat Inc',
    'website': 'https://www.openeducat.org',
    'depends': [
        'website_forum',
        'openeducat_lms',
    ],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'views/course_view.xml',
        'views/lms_forum_view.xml',
    ],
    'demo': [
        'demo/op_course_forum_data.xml',
    ],
    'images': [
        'static/description/openeducat_lms_forum_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'Other proprietary',
}
