# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Fields Manager',
    'version': '18.0.0.0',
    'summary': 'This module help add new custom field for all objects and add new tab in form view ',
    'description': """This module help add new custom field for all objects and add new tab in form view""",
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://candidroot.com/",
    'category': 'web',
    'depends': ['web'],
    'images':  ['static/description/banner.png'],
    'data': [
        'security/manager_security.xml',
        'security/ir.model.access.csv',
        'views/model_views.xml',
        'views/create_custom_tab_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'all_model_custom_fields_cr/static/src/js/form_controller.js',
        ],
    },
    'price': 24.99,
    'currency': 'USD',
    'live_test_url': 'https://youtu.be/-WluBCG8dRE',
    'installable': True,
    'auto_install': False,
    'application': False,
}
