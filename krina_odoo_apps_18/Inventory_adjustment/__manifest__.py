{
    'name': 'Inventorty - Adjustment Report',
    'category': 'Inventory',
    'description': """ Inventory Adjustment Report""",
    'summary': """Inventory Adjustment Report""",
    'author': 'Candidroot Solution Pvt. Ltd.',
    'website': 'https://candidroot.com',
    'license': 'LGPL-3',
    'version': "18.0.0.0",
     'depends': ['base','stock'],
     'data': [
          'security/ir.model.access.csv',
          'views/blank_pdf.xml',
          'wizard/inventory_adjustment_wizard_view.xml',
     ],
     'installable': True,
    'application': False,
}