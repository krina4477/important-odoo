{
    'name' : "Inventory Transfer Report",
    'version' : "18.0.0.1",
    'category' : "Extra Tools",
    'author': 'Candidroot Solutions Pvt. Ltd.',
    'website': 'https://www.candidroot.com',
    'summary': 'Inventory Transfer Report',
    'description' : '''
             Inventory Transfer Report. 
    ''',
    'depends' : ['base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/inventory_transfer_report.xml',
        'report/inventory_transfer_report_pdf.xml',
             ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license':'LGPL-3'

}
