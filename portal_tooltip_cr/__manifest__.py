{
    'name': 'Portal Tooltip',
    'version': '18.0.0.1',
    'description': """
        Instantly view detailed information by hovering your mouse over document references in the Odoo portal.
        This module adds dynamic popovers for Sale Orders, Invoices, Purchase Orders, and RFQs, allowing portal users to preview order lines and key details without navigating away from the list view. Enhance your portal experience with quick, interactive tooltips for all major business documents.
    """,
    'category': 'Website',
    'author': 'Candidroot Pvt.Ltd.',
    'website': 'https://www.candidroot.com/',
    'depends': [
        'website_sale', 'website', 'sale_management', 'sale', 'account', 'purchase'
    ],
    'assets': {
        'web.assets_frontend': [
            'portal_tooltip_cr/static/src/js/popover.js',
            'portal_tooltip_cr/static/src/css/popover.css',
        ],
    },
    'data': [
        'views/sale_order_popover.xml',
        'views/account_popover.xml',
        'views/purchase_popover.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
