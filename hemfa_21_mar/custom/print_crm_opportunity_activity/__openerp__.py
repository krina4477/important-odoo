# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Print CRM Lead Opportunity Pipeline',
    'version': '5.1.4',
    'price': 15.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Sales',
    'summary': 'This module allow user to print CRM Opportunity Activity in pdf format.',
    'description': """
This module allow user to print CRM Opportunity Activity in pdf format.
Tags:
print CRM Opportunity Activity
CRM Opportunity Activity
Opportunity Activity PDF
Opportunity Activity qweb
print crm
print Opportunity
print lead
print activity
report on lead
report on Opportunity
report on activity
print pipeline
pipeline crm print
crm logs print
            """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'depends': ['crm', 'sale_crm'],
    'images': ['static/description/img.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/print_crm_opportunity_activity/737',#'https://youtu.be/YZqSs9PsOf0',
    'data': [
             'views/report_reg.xml',
             'views/report_crm_opportunity_activity.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
