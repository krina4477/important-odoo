# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Auto Send Payslip to Employee",
    'category': 'Human Resources',
    'summary': """Auto Send Payslip to Employee""",
    'version': '18.0.0.1',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'sequence': 2,
    'description': """This module allows you to send salary slip report to employee of previous month.""",
    'depends': ['hr', 'hr_payroll'],
    'data': [
        'data/payslip_cron.xml',
        'data/payslip_mail_template.xml',
    ],
    'qweb': [],
    'images' : ['static/description/banner.png'],
    'installable': True,
    'price': 7,
    'currency': 'USD',
    'auto_install': False,
    'application': True,
}
