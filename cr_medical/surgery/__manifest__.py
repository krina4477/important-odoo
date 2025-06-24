# -*- coding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'CR Medical Surgery',
    'version': '15.0.0.1',
    'summary': 'Medical CR Surgery Management',
    'sequence': 7,
    'description': """

    """,
    'category': 'Surgery',
    'depends': ['base', 'cr_medical_base', 'IPD'],

    'website': 'https://www.candidroot.com/',
    'author': "Candidroot Solutions Pvt. Ltd.",

    'data': [
        'security/ir.model.access.csv',
        'views/inherit_ipd_registration_view.xml',
        'views/surgery_type_view.xml',
        'views/show_surgery_ipd_view.xml',
        'wizard/ipd_surgery.xml',
        'wizard/surgery_report.xml',
        'report/surgery_reports.xml',
        'report/surgery_department_wise_template.xml',
        'report/surgery_reports_template.xml',
        'report/surgery_doctor_wise_template.xml',
        'report/surgery_diseases_wise_report.xml',

        'data/surgery_demo_data.xml',

    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
