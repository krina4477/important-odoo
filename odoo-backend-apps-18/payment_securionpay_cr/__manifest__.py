# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Securionpay Payment Acquirer',
    'version': '18.0.0.1',
    'summary': """
        Securionpay Payment Acquirer
    """,
    'description': """

Securionpay Payment Acquirer
============================
Securionpay Payment Acquirer

Description
-----------
    - This module will allow user can payment using Securionpay Payment Acquirer.

    """,
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://www.candidroot.com/",
    'depends': ['website_sale'],
    'data': [
        'views/payment_securionpay_templates.xml',
        'data/payment_acquirer_data.xml',
        'data/payment_provider_data.xml',
        'views/payment_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_securionpay_cr/static/src/js/payment_form.js',
        ],
    },
    'license':'LGPL-3',
    'images': ['static/description/SecurionPay Payment Acquirer.jpg'],
    'price':49.99,
    'live_test_url': 'https://youtu.be/t8Uy99b2xGI',
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False
}

