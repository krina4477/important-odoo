# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Product Deposit Management",

    'summary': """
        This module allows you to manage deposit for beverages product""",

    'description': """
        This module allows you to manage deposit for beverages product
    """,

    'author': 'Candidroot Solutions Pvt. Ltd.',
    'website': 'https://www.candidroot.com',
    'category': 'Sales',
    'version': '18.0.0.2',
    'depends': ['product', 'account', 'sale_management', 'sale_stock', 'purchase_stock'],
    'data': [
        'data/product_data.xml',
        'views/product_template_views.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/res_partner_view.xml',
        'views/product_packaging_view.xml',
        'views/stock_picking_view.xml',
        'views/account_move_line_view.xml',
        'views/account_move_report_inherit_views.xml',
        'views/purchase_order_report_inherit_views.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.jpeg'],
    'installable': True,
    'live_test_url': 'https://youtu.be/8aHm0lVGPCo',
    'price': 50,
    'currency': 'USD',
    'auto_install': False,
    'application': True,
}
