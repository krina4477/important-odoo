# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


{
    'name': "Dynamic Search Filter",
    'description': """
        This module adds an extra option in Add Custom Filter using which you can add the field in default option .""",
    'category': 'Other',
    'version': '18.0.0.1',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'depends': ['base','web'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'dynamic_search_filter_cr/static/src/js/filter_button.js',
            'dynamic_search_filter_cr/static/src/js/custom_search.js',
            'dynamic_search_filter_cr/static/src/xml/filter_button.xml',
        ],
    },

    'images': ['static/description/banner.jpeg'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
