# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Purchase Order Automation",
    'category': 'Purchase',
    'summary': """Purchase Order Automation for odoo community version and odoo enterprisee version.""",
    'version': '18.0.0.1',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'sequence': 2,
    'description': """This module allows you to create and validate picking, create bills and register the payment on one click.""",
    'depends': ["base", "purchase_stock", "account"],
    'data': [
        'views/res_users_view.xml',
    ],

    'qweb': [],
    'images' : ['static/description/banner.png'],
    'installable': True,
    'live_test_url': 'https://youtu.be/qFnZWMB46DQ',
    'price': 19.99,
    'currency': 'USD',
    'auto_install': False,
    'application': False,
}
