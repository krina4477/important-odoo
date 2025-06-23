# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Leave Portal',
    'version': '18.0.0.1',
    'summary': 'Request Time Off Through Odoo Portal',
    'category': "Human Resources",
    'author': 'Candidroot Solutions Pvt. Ltd.',
    'website': 'https://www.candidroot.com',
    'sequence': 20,
    'description': """
            This user-friendly module allows employees to seamlessly request leave directly through the Odoo portal using their login credentials.
            Employees can submit leave requests, track their status, and view their leave balance,all from the convenience of the portal interface.
    """,
    'depends': [
        'hr','portal','hr_holidays','website','mail','calendar','web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_portal_view.xml',
        'views/hr_employee_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'hr_leave_portal_cr/static/src/js/leave_btn.js',
        ],
    },
    'images': ['static/description/banner.jpg'],
    'price': 199.0,
    'currency': 'USD',
    'live_test_url': 'https://youtu.be/Ay5fX0YxDyE',
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
