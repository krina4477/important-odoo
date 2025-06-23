# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Account Partner Auto Reconcile",
    'category': 'Accounting/Accounting',
    'summary': """Account Partner Auto Reconcile.""",
    'version': '18.0.0.3',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'sequence': 2,
    'description': """This module allows you to automatically reconcile all the customer invoices and vendor bills with just one click.""",
    'depends': ['account_reports'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_partner_auto_reconcile_cr/static/src/js/account_reports.js'
        ]
    },
    'qweb': [],
    'images' : ['static/description/banner.png'],
    'installable': True,
    'live_test_url': 'https://www.youtube.com/watch?v=spkkPDPS5Ow',
    'price': 49.99,
    'currency': 'USD',
    'auto_install': False,
    'application': False,
}
