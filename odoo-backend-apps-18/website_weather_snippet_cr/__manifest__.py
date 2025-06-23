# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Weather Snippet',
    'version': '18.0.0.1',
    'summary': 'Website Weather Snippet',
    'description': """CandidRoot Solutions with a feature that introduce new 'Weather Widget' for odoo website.""",
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://candidroot.com/",
    'category': 'Website/Website',
    'depends': ['website', 'base_geolocalize'],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/weather_city.xml',
        'views/weather_snippet.xml',
    ],
    'assets': {
        'website.assets_wysiwyg': [
            'website_weather_snippet_cr/static/src/js/option_1.js',
        ],
    },
    'price': 24.99,
    'currency': 'USD',
    'live_test_url': 'https://youtu.be/tXI3t7VXUvs',
    'installable': True,
    'auto_install': False,
    'application': False,
}
