# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Find Record With Same Value',
    'category': 'Web',
    'summary': 'This module will add widget and it will help you to find the same value in same Object.',
    'version': '18.0.0.0',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'sequence': 3,
    'description': """This module will add widget and it will help you to find the same value in same Object.""",
    'depends': ['web'],
    'demo': [],
    'qweb': [],
    'assets': {
        'web.assets_backend': [
            '/find_record_with_same_value_cr/static/src/xml/base_web.xml',
            '/find_record_with_same_value_cr/static/src/js/basic.js',
            '/find_record_with_same_value_cr/static/src/css/style.scss',
        ],
    },
    'license': 'LGPL-3',
    'images' : ['static/description/banner.png'],
    'installable': True,
    'live_test_url': 'https://youtu.be/Qey3SdYGQWg',
    'price': 9.99,
    'currency': 'USD',
    'auto_install': False,
    'application': True,
}