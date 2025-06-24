# -*- encoding: utf-8 -*-
##############################################################################
#    Module Writen to odoo
#
#    Copyright (C) 2016 - Today Icap Inc. <http://www.icapsystems.com>
#
#    @author Turkesh Patel
##############################################################################
{
    "name": "Google Merchant Center Integration", 
    "version": "1.0", 
    "author": "Icap Inc.", 
    'license': 'OPL-1',
    "category": "Website", 
    "summary": """This module adds funtionality to syncronize product details on your Google merchant center account""",
    "description": """
 Google Merchant Center Integration
===================================

This module adds funtionality to syncronize product details on your Google merchant center account.
""", 
    "website": "http://www.icapsystems.com", 
    "depends": ["website_sale"], 
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        "data/product_data.xml",
        "views/product_views.xml",
        "views/gmc_views.xml",
        "views/template.xml",
        "views/res_config_view.xml",
        "views/menu_item.xml",
    ],
    'images': [
        'static/description/integration.png',
    ],
    "installable": True, 
    "price": 150,
    "currency": "USD",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: