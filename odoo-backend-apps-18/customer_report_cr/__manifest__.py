# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Customer Report',
    'category': 'base',
    'summary': 'Customer Report',
    'version': '18.0.0.1',
    'website': "https://www.candidroot.com/",
    'author': "Candidroot Solutions Pvt. Ltd.",
    'description': """This module helps to create report in Partner.""",
    'sequence':8,
    'depends': ['sale_management','account','project','purchase','account_check_printing'],
    'data': [
        'security/security_access.xml',
        'report/header_footer.xml',
        'report/report_template.xml',
        'report/report_menu.xml'
    ],
    'images' : ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'live_test_url': 'https://youtu.be/HnvncXtCWPc',
    'price': 9.99,
    'currency': 'USD',
    'auto_install': False,
    'application': True,

}