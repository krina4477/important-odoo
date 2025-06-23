# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    "name": "Invoice Multi Approval",
    "version": "18.0.0.0",
    'author': 'Candidroot Solutions Pvt. Ltd.',
    'website': 'https://www.candidroot.com',
    'category': 'Accounting',
    'description': """
        This module allows to add multi level approval for the Invoices.
        """,
    "depends": ['base', 'product', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/invoice_approval_mail_template.xml',
        'views/approval_config.xml',
        'views/account_invoice.xml',
    ],
    'images': ['static/description/banner.jpeg'],
    'live_test_url': 'https://youtu.be/DRVIGSSeim0',
    'price': 29.99,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

