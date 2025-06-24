# -*- coding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'CR Medical Diet',
    'version': '15.0.0.1',
    'summary': 'Medical CR Diet Management',
    'sequence': 4,
    'description': """

    """,
    'category': 'Diet',
    'depends': ['base', 'cr_medical_base', 'IPD', 'board'],

    'website': 'https://www.candidroot.com',
    'author': "Candidroot Solutions Pvt. Ltd.",

    'data': [
        'security/ir.model.access.csv',
        'views/break_fast_views.xml',
        'views/lunch_info_views.xml',
        'views/dinner_info_views.xml',
        'views/ipd_summary.xml',
        'wizard/diet_plan_views.xml',
        'views/kitchen_details_views.xml',
        'views/ipd_registration_form_views.xml',
        'views/diet_dashboard.xml',
        'data/diet_demo_data.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
