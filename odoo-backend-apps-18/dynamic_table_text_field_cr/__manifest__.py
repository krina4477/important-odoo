# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Dynamic Table Text Field',
    'category': 'Web',
    'summary': 'This module allow user to add Columns & Rows on the fly using odoo widget ',
    'version': '18.0.0.1',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'sequence': 3,
    'description': """This module allow user to add Columns & Rows on the fly using odoo widget""",
    'depends': ['web','sale_management'],
    'demo': [],
    'data': [
        'views/widget.xml'
    ],
    'qweb': [],
    'assets': {
        'web.assets_backend': [
            'dynamic_table_text_field_cr/static/src/js/basic.js',
            'dynamic_table_text_field_cr/static/src/js/dialog.js',
            'dynamic_table_text_field_cr/static/src/js/save_discard.js',
            'dynamic_table_text_field_cr/static/src/xml/base_web.xml',
            'dynamic_table_text_field_cr/static/src/css/style.scss',
            'dynamic_table_text_field_cr/static/src/lib/jquery.min.js',
        ],
    },
    'license': 'LGPL-3',
    'images' : ['static/description/banner.png'],
    'installable': True,
    'live_test_url': '',
    'price': 9.99,
    'currency': 'USD',
    'auto_install': False,
    'application': True,
}
