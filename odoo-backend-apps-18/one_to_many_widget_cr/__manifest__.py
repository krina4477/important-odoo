# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Download Excel (one2Many Widget)',
    'version': '18.0.0.0',
    'category': 'Extra Tools',
    'author': 'Candidroot Solutions Pvt. Ltd.',
    'website': 'https://www.candidroot.com',
    'summary': 'This module will helps you to download excel data of all one2many field',
    'description': """
                    After applying widget to the one2many field you will find one button above
                    one2many field and you can download lines data in excel by clicking that button.
                    """,
    'depends': ['base'],
    'assets': {
        'web.assets_backend': [
            'one_to_many_widget_cr/static/src/js/fields.js',
            'one_to_many_widget_cr/static/src/xml/one2manywidget_template.xml',
        ],
    },
    'demo': [],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'price': 19.99,
    'currency': 'USD',
    'live_test_url': 'https://youtu.be/081428kIEGg',
    'installable': True,
    'auto_install': False,
    'application': False
}
