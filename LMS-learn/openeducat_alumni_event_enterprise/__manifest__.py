# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

{
    'name': 'OpenEduCat Alumni Event Enterprise',
    'summary': 'Adds alumni events management to OpenEduCat.',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'sequence': 3,
    'author': 'OpenEduCat Inc',
    'website': 'https://www.openeducat.org',
    'depends': [
        'base',
        'website_event',
        'openeducat_alumni_enterprise',
    ],
    'data': [
        'menus/op_menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
}
