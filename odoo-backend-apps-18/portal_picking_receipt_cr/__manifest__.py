# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Portal Picking Receipt',
    'version': '18.0.0.1',
    'summary': 'Portal Picking Receipt',
    'description': """This module allows portal user to print Picking receipt from my account view.""",
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://candidroot.com/",
    'category': 'Picking',
    'depends': ['sale_stock'],
    'images': ['static/description/banner.jpeg'],
    'data': [
        'views/portal_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/portal_picking_receipt_cr/static/src/scss/portal.scss',
        ]
    },
    'price': 24.99,
    'currency': 'USD',
    'live_test_url': 'https://youtu.be/tp3IF0azzZU',
    'installable': True,
    'auto_install': False,
    'application': False,
}
