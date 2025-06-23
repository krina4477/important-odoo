{
    'name': 'Price & Quantity Checker',
    'version': '1.3',
    'summary': 'Scan product barcodes to check stock levels and pricing dynamically across multiple warehouses.',
    'description': """
        A comprehensive price and quantity checker module for Odoo that:
        - Scans barcodes to fetch product variants and attributes.
        - Displays stock availability per warehouse.
        - Retrieves real-time pricing from the selected pricelist.
        - Allows filtering stock by warehouse selection.
        - Automatically clears barcode field after scanning.
        - Dynamically updates stock information based on selected warehouse.
    """,
    'author': 'Loai Souboh',
    'category': 'Inventory',
    'depends': ['product', 'stock'],
    'data': [
        'security/ir.model.access.csv',  # ✅ Security settings
        'views/price_checker_view.xml',  # ✅ Main view
    ],
    'assets': {
        'web.assets_backend': [
            'price_checker/static/src/scss/hide_button.scss',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
