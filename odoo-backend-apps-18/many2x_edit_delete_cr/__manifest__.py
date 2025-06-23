# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Many2x Edit / Delete on Selection",
    'summary': """
        This module will enhance many2one and many2many field widget to perform delete and edit action from dropdown.""",

    'description': """
    
Many2x Edit / Delete on Selection
=================================
Many2x Edit / Delete on Selection

Description
----------- 

- This module will enhance many2one and many2many field widget to perform delete and edit action from dropdown,
  that will be configurable to enable/disable feature.

- Delete/Edit button will display based on access rights.

    """,

    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://candidroot.com/",
    'category': 'Extra Tools',
    'version': '18.0.0.1',
    'depends': ['base', 'web', 'partner_autocomplete'],
    'images': ['static/description/many2x.jpg'],
    'license': 'OPL-1',
    'price': 14.99,
    'currency': 'EUR',
    'live_test_url': 'https://youtu.be/TCZN8JtJO0g',
    'installable': True,
    'auto_install': False,
    'application': False,
    'assets': {
        'web.assets_backend': [
            'many2x_edit_delete_cr/static/src/js/many2x.js',
            'many2x_edit_delete_cr/static/src/js/x2many.js',
            'many2x_edit_delete_cr/static/src/js/autocomplete.js',
            'many2x_edit_delete_cr/static/src/js/select_dialog.js',
            'many2x_edit_delete_cr/static/src/xml/many.xml',
            'many2x_edit_delete_cr/static/src/css/style.css'
        ]
    }
}
