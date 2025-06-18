
{
    'name': 'Credit Negative Stock Report',
    'version': '18.0.0.0',
    'description': '',
    'summary': 'Report for products that have Negative',
    'author': '',
    'website': '',
    'license': 'LGPL-3',
    'category': 'Sales',
    'depends': [
        'sale', 'stock'
    ],
    'data': [
        'security/ir.model.access.csv',

        'wizards/credit_negative_stock_report_wizard_views.xml',
        'reports/credit_negative_stock_report_template.xml',
    ],
    'auto_install': False,
    'application': False,
}