# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Notification of Journal Entry Creation",
    'category': 'Accounting/Accounting',
    'summary': """Notification of Journal Entry Creation""",
    'version': '18.0.0.1',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'description': """This module allows user to get notified on top right corner as soon as Journal Entry created.""",
    "depends": ["web", "bus", "base", "mail","sale"],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'acc_move_notify_cr/static/src/js/notification_esm.js',   
            'acc_move_notify_cr/static/src/js/notification_services.js',
        ],
    },
    'qweb': [],
    'images' : ['static/description/banner.jpeg'],
    'installable': True,
    'live_test_url': 'https://youtu.be/qPGQuKYv5vE',
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}