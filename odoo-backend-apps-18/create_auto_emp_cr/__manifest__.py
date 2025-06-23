# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Auto Create Employee",
    'category': 'Extra Tools',
    'summary': """Auto create employee based on creation of user.""",
    'version': '18.0.0.1',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'sequence': 2,
    'description': """This module allows you to create employee automatically while creating users""",
    'depends': ["base", "hr"],
    'data': [
        'views/res_config_settings_views.xml',
        'views/res_users_view.xml'
    ],
    'qweb': [],
    'images' : ['static/description/banner.png'],
    'installable': True,
    'live_test_url': 'https://youtu.be/Y_PwdxaNxeY',
    'price': 9.99,
   'currency': 'USD',
    'auto_install': False,
    'application': False,
}
