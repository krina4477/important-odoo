# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    "name": "Indian Quarter Date Filter",
    "summary": "Indian Quarter Date Filter",
    "category": "Filter",
    "version": "18.0.0.0",
    "author": "CandidRoot Solutions",
    "website": "https://candidroot.com/",
    "description": """ """,
    "depends": ['base', 'web'],
    'images': ['static/description/banner.jpg'],
    "data": [],
    "demo": [],
    'assets': {
        'web.assets_backend': [
            'indian_quarter_date_filter_groupby/static/src/js/date.js',
            'indian_quarter_date_filter_groupby/static/src/js/searchmodel.js',
        ],
    },
    "installable": True,
    'application': True, 
    'license': 'OPL-1',
    'live_test_url': '',
    'price': 24.99,
    'currency': 'USD',
}
