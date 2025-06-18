# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Cr Default Customerprice_list_ret_id",
    "version" : "18.0.0.1",
    "category" : "Point of Sales",
    "depends" : ['base','point_of_sale'],
    "author": "",
    'summary': "",
    "description": """""",
    "data": [
        'views/pos_config_views.xml'
    ],
     'assets': {
         'point_of_sale._assets_pos': [
             'pos_default_customer_cr/static/src/js/Chrome.js',
         ],
     },
    "auto_install": False,
    "installable": True,
    'license': 'OPL-1',
}