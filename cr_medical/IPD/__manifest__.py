# -*- coding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'CR Medical IPD',
    'version': '15.0.0.1',
    'summary': 'Medical CR Medical Management',
    'sequence': 4,
    'description': """
    
    """,
    'category': 'IPD',
    'depends': ['base', 'cr_medical_base', 'website'],

    'website': 'https://www.candidroot.com',
    'author': "Candidroot Solutions Pvt. Ltd.",

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/ipd_report.xml',
        'wizard/admit_patient_view.xml',
        'report/ipd_reports.xml',
        'report/medicine_report_department.xml',
        'report/ipd_department_wise_template.xml',
        'report/ipd_report_month_template.xml',
        'report/ipd_medicine_patient_template.xml',
        'report/ipd_patient_count_report_template.xml',
        'report/ipd_reports_template.xml',
        'report/ipd_discharge_summary_template.xml',
        'report/ipd_bed_count_template.xml',
        'views/room.xml',
        'views/opd_view.xml',
        'views/room_facilities.xml',
        'views/room_type.xml',
        'views/ipd_registration_form_view.xml',
        'views/website_demo.xml',
        'views/res_partner_patient_inherit.xml',
        'data/ipd_demo_data.xml',

        'data/ipd_demo_data.xml',

    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
