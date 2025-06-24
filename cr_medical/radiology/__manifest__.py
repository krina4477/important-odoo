# -*- encoding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'CR Medical Radiology',
    'summary': 'Medical CR Radiology Management',
    'version': '15.0.0.1',
    'category': 'Radiology',
    'sequence': 4,
    'website': 'https://www.candidroot.com/',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'description': """

    """,
    'depends': ['base', 'cr_medical_base'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/radiology_view.xml',
        'views/radiologist_view.xml',
        'views/radio_test_type_view.xml',
        'views/patient_radio_test_view.xml',
        'views/radio_test_price_view.xml',
        'views/radiologist_education_view.xml',
        'data/radiology_demo_data.xml',

        'data/radiology_demo_data.xml',

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
