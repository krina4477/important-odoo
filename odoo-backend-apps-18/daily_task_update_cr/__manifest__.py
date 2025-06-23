# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name' : "Daily Task Updates to Manager",
    'version' : "18.0.0.0",
    'category' : "Extra Tools",
    'license': 'OPL-1',
    'summary': 'Send daily task updates to Manager',
    'description' : '''
        Module to send daily task updates to Manager end of the day.
    ''',
    'author': 'Candidroot Solutions Pvt. Ltd.',
    'website': 'https://www.candidroot.com',
    'depends' : ['project'],
    'data': [
         'data/ir_cron_data.xml',
         'data/daily_task_update_template.xml',
         'views/project_task_inherit_view.xml'
             ],
    'images' : ['static/description/Banner.png'],
    'price': 4.99,
    'currency': 'USD',
    'live_test_url': 'https://youtu.be/krPDwDjLJrs',
    'installable': True,
    'auto_install': False,
    'application': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
