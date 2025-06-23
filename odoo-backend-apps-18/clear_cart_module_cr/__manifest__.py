# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Clear Cart Module',
    'category': 'ecommerce',
    'summary': 'Website Clear Cart',
    'version': '18.0.0.1',
    'website': "https://www.candidroot.com/",
    'author': "Candidroot Solutions Pvt. Ltd.",
    'description': """This module helps to Clear Cart in website.""",
    'sequence':8,
    'depends': [
        'website_sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/shop_cart.xml'
    ],
    'images' : ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'live_test_url': 'https://youtu.be/vTkXK8XT_k8',
    'price': 4.99,
    'currency': 'USD',
    'auto_install': False,
    'application': True,
}
