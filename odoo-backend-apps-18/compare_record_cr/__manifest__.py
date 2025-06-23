# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Compare Values of Two Sales Order Records',
    'version': '18.0.0.1',
    'description': """
        This module allows user to Compare values for two selected Sales Orders.
    """,
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://www.candidroot.com/",
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'wizard/wiz_compare_record.xml',
    ],
    'qweb': [],
    'images' : ['static/description/banner.jpeg'],
    'installable': True,
    'live_test_url': 'https://youtu.be/C8uSipOn7oA',
    'price': 9.99,
    'currency': 'USD',
    'auto_install': False,
    'application': False,
}
