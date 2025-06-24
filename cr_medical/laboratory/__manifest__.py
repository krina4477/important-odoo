# -*- coding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'CR Medical Laboratory',
    'version': '15.0.0.1',
    'summary': 'Medical CR Laboratory Management',
    'sequence': 3,
    'category': 'Laboratory',
    'website': 'https://www.candidroot.com/',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'description': """
    
    """,
    'depends': ['cr_medical_base'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/laboratory.xml',
        'views/pathologist_view.xml',
        'views/pathologist_education_view.xml',
        'views/lab_test_price_view.xml',
        'views/lab_test_type_view.xml',
        'views/lab_patient_lab_test_view.xml',
        'data/laboratory_demo_data.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
