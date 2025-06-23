# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Expand Messages In Discuss',
    'version': '18.0.0.1',
    'sequence': 1,
    'category': 'Discuss',
    'summary': 'Expand Messages',
    'author': 'Candidroot Solutions Pvt. Ltd.',
    'website': 'https://www.candidroot.com',
    'description': "This module will help you to expand long message using 'See More' in discuss app.",
    'depends': ['mail','web'],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'expand_messages_cr/static/src/components/message.scss',
            'expand_messages_cr/static/src/components/message.js',
            'expand_messages_cr/static/src/components/message.xml'
        ],
    },
    'demo': [

    ],
    'images': ['static/description/banner.png'],
    'live_test_url': 'https://youtu.be/xBt3RbkWTRI',
    'price': 9.99,
    'currency': 'USD',
    'auto_install': False,
    'application': False,
}
