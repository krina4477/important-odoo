# -*- encoding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'CR Medical Pharmacy',
    'summary': 'Medical CR Pharmacy Management',
    'version': '15.0.0.1',
    'category': 'Pharmacy',
    'sequence': 4,
    'website': 'https://www.candidroot.com/',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'description': """

    """,
    'depends': ['product', 'cr_medical_base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/pharmacy_view.xml',
        'views/pharmacist_view.xml',
        'views/pharmacist_education_view.xml',
        'views/pharmacy_product_view.xml',
        'data/pharmacy_demo_data.xml',

        'data/pharmacy_demo_data.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
