# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Add A Field In List View',
    'version': '18.0.0.0',
    'category': 'Extra Tools',
    'website': "https://www.candidroot.com/",
    'author': "Candidroot Solutions Pvt. Ltd.",
    'summary': 'Add a field in list view',
    'description': """ This module will help you to add new 
        fields in the list view and it will allow you to 
        add the fields for Sales, CRM, Invoice, Products etc.""",
    'depends': ['web'],
    "installable": True,
    'application': True,
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'live_test_url': 'https://youtu.be/Q6nfrtR3SGw',
    'price': 29.99,
    'currency': 'USD',
    'assets': {
        'web.assets_backend': [
            ('after', 'web/static/src/views/list/list_renderer.xml', 'add_list_view_field_cr/static/src/views/list/list_renderer.xml'),
            'add_list_view_field_cr/static/src/views/list/list_renderer.js',
            'add_list_view_field_cr/static/src/css/button.css',
        ]
    }

}
