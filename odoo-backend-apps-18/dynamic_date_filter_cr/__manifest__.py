# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Dynamic Date Filter",

    'summary': """ Dynamic Date Filter """,
    'version': '18.0.0.1',
    'description': """
Description
-----------
    - Candidroot Dynamic Date filter

    """,
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://candidroot.com/",
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/dynamic_date_filter_views.xml',
    ],
    'images': ['static/description/Banner.png'],
    'license': 'OPL-1',
    'demo': [
    ],
    'price': 49.99,
    'currency': 'EUR',
    'installable': True,
    'live_test_url': 'https://youtu.be/RqXFu2zIO9Q',
    'auto_install': False,
    'application': False
}
