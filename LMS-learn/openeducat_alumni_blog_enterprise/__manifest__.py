# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Alumni Blog Enterprise',
    'summary': """This module adds the feature of blog in alumni management system
     to OpenEduCat. You can create blog and post it online.""",
    'version': '19.0.1.0.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': ['base', 'website_blog', 'openeducat_alumni_enterprise'],
    'data': ['views/alumni_view.xml',
             'views/alumni_blog_template_view.xml',
             'menus/op_menu.xml'
             ],
    'demo': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
