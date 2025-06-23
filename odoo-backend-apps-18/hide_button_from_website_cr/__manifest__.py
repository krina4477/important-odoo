# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Hide Price,Add To Cart Button, Quantity From website',
    'category': 'eCommerce',
    'summary': 'Hide the price,Add TO Cart Button and Quantity of the product if user is not login',
    'version': '18.0.0.1',
    'website': "https://www.candidroot.com/",
    'author': "Candidroot Solutions Pvt. Ltd.",
    'description': """This module helps to Hide the price,Cart Button and quantity of the product if user is not login.""",
    'sequence':8,
    'depends': [
        'website_sale'
    ],
    'data': [
        'views/website_template_inherit.xml'
    ],
    'images' : ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'live_test_url': 'https://youtu.be/-pPmwGttepI',
    'price': 39.99,
    'currency': 'USD',
    'auto_install': False,
    'application': True,
}
