# -*- coding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'CR Medical Reception',
    'version': '15.0.0.1',
    'summary': 'Medical CR Medical Management',
    'sequence': 5,
    'description': """
    
    """,
    'category': 'Reception',
    'depends': ['base', 'cr_medical_base', 'website'],

    'website': 'https://www.candidroot.com',
    'author': "Candidroot Solutions Pvt. Ltd.",

    'data': [
        'security/security.xml',
        'views/receptionist_view.xml',
        'data/reception_demo_data.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
