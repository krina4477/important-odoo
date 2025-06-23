# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Delete Posted Journal Entry',
    'category': 'Accounting',
    'summary': "Delete Posted Journal Entry",
    'version': '18.0.0.1',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'description': """This Module allows you to delete journal entry after post""",
    'depends': ['account'],
    'demo': [],
    'data': [
            'security/manager_security.xml',
            'views/move_view.xml',
            ],
    'qweb': [],
    'license': 'OPL-1',
    'installable': True,
    'images' : ['static/description/banner.png'],
    'live_test_url': 'https://youtu.be/CodPkBa1QUI',
    'price': 9.99,
    'currency': 'USD',
    'auto_install': False,
    'application': True,

}

