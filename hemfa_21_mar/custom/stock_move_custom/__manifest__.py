{
    'name': 'Stock Move Customization',
    'version': '1.0',
    'category': 'Inventory',
    'author': 'Loai Souboh',
    'summary': 'Add custom column for (Done - Demand) in stock move lines',
    'description': 'Calculates and displays the difference between Done and Demand in stock moves.',
    'depends': ['stock'],
    'data': [
        'views/stock_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
