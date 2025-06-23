# -*- coding: utf-8 -*-

###############################################################################
{
    'name': 'POS Restriction For Zero Quantity.',
    'version': '16.0.1.0.3',
    'category': 'Point of Sale',
    'summary': 'This module will restrict zero quantity confirmation in POS.',
    'description': """This module will help you to avoid zero quantity 
                        confirmation in POS. It will show warning if zero 
                        quantity confirmation occurred.""",
    'author': '',
    'company': '',
    'maintainer': '',
    'website': "https://www.cybrosys.com",
    'images': ['static/description/banner.jpg'],
    'depends': ['base', 'point_of_sale','sh_pos_all_in_one_retail'],
    'data':['views/inherit_product_template_view.xml'],
    'assets': {
        'point_of_sale.assets': [
            'pos_zero_quantity_restrict/static/src/js/**/*.js',
        ]
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
