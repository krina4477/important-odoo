# -*- coding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'CR Medical Physiotherapy',
    'version': '15.0.0.1',
    'summary': 'Medical CR Physiotherapy Management',
    'sequence': 6,
    'description': """

    """,
    'category': 'Physiotherapy',
    'depends': ['base', 'cr_medical_base', 'IPD'],

    'website': 'https://www.candidroot.com/',
    'author': "Candidroot Solutions Pvt. Ltd.",

    'data': [
        'security/ir.model.access.csv',
        'views/ipd_registration_inherit_view.xml',
        'views/inherit_ipd_summary_views.xml',
        'views/show_ipd_physiotherapy_views.xml',
        'wizard/ipd_physiotherapy.xml',
        'data/physiotherapy_demo_data.xml',

    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
