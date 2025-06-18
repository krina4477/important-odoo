# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Warehouse Set configration",
    'category': '',
    'summary': """Warehouse Set Config Automation for odoo community version and odoo enterptrise version.""",
    'version': '18.0.0.1',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'sequence': 2,
    'description': """This module allows you to Automatically select warehouse based on customer address (zip code) for fast delivery.""",
    'depends': ["base", "sale", "stock"],
    'data': [
        'views/inherit_stock_warehouse.xml',
    ],
    'qweb': [],
    'installable': True,
    'currency': 'USD',
    'auto_install': False,
    'application': False,
}
