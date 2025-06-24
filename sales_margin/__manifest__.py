# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Sales Margin Calculation',
    'version': '16.0.0.1',
    'summary': 'It is use for calculating margins',
    'description': ''' This module is made for calculate margin on products in sales and invoices for specific groups''',
    'category': 'Sales',
    'author': 'Candidroot Solutions Pvt. Ltd.',
    'website': 'www.candidroot.com',
    'license': 'LGPL-3',
    'depends': ['sale_management', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'report/sale_margin_report.xml',
        'report/sale_margin_report_template.xml',
        'wizard/sale_margin_wizard_view.xml',
        'views/inherit_sale_order_line_view.xml',
        'views/inherit_account_move_line_view.xml',
        'views/inherit_sale_order_view.xml',
        'views/inherit_account_move_view.xml',
        'views/inherit_product_view.xml',
        'views/inherit_sale_margin_report_menu.xml',
    ],
    'demo': [''],
    'installable': True,
    'auto_install': False,

}