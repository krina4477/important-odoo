# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Account Sequence Based on Fiscal Year",
    'description': " This module allows you to manage sequence based on defined fiscal year for your business as per country specific rules. ",
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://candidroot.com/",
    'category': 'Accounting',
    'version': '18.0.0.1',
    'depends': ['accountant'],
    'data': [
        "views/res_config_settings_views.xml",
    ],
    'images': ['static/description/banner.JPEG'],
    'license': 'OPL-1',
    'price': 29.99,
    'currency': 'USD',
    'live_test_url': 'https://youtu.be/NK7cA_wKeD8',
    'installable': True,
    'auto_install': False,
    'application': False,
}
