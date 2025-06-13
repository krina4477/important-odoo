# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Dynamic Dashboard',
    'version': '18.0.0.0',
    'summary': 'Generic KPI Dashboard',
    'description': 'Displays dynamic metrics and charts from common Odoo models.',
    'category': 'Tools',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_section.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dynamic_dashboard_cr/static/src/js/dynamic_dashboard.js',
            'dynamic_dashboard_cr/static/src/xml/dashboard_templates.xml',
            'dynamic_dashboard_cr/static/src/scss/dynamic_dashboard.scss'
        ],
    },
    'installable': True,
    'application': True,
}
