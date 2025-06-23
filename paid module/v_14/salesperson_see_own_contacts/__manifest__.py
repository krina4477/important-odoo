# -*- coding: utf-8 -*-
{
    'name':
    "Restrict Salespersons To Own Contacts Only",
    'license':
    'OPL-1',
    'support':
    'support@optima.co.ke',
    'summary':
    """
        Restrict your salespersons to access their own contacts (customers and vendors) only.""",
    'description':
    """
         A module to restrict your salespersons or salesmen and saleswomen to be able ``see`` and ``edit`` their own contacts (customers and vendors). It also allows the salespersons to ``see`` and ``edit`` contacts to which they have been added as ``followers`` of those contacts.
    """,
    'author':
    "Optima ICT Services LTD",
    'website':
    "http://www.optima.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category':
    'Sales',
    'version':
    '12.0.0.2',
    'price':
    59,
    'currency':
    'EUR',

    # any module necessary for this one to work correctly
    'depends': ['sales_team'],

    # always loaded
    'data': [
        'security/res.groups.csv',
        'security/ir.rule.csv',
        'security/ir_rule.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'application':
    True,
}
