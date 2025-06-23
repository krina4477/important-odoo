{
    'name': 'Custom Stock Extension',
    'version': '1.2',
    'depends': ['stock', 'stock_account'],
    'author': 'Loai Souboh',
    'category': 'Warehouse',
    'description': """
    Customizations for Stock Picking and Stock Valuation Layer.
    """,
    'data': [
        'security/security.xml',             # Include the security group definition
        'views/stock_picking_views.xml',      # Include the XML view file here
    ],
    'installable': True,
    'application': False,
}
