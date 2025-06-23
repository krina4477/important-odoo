{
    'name': 'Two-Step Internal Transfer',
    'version': '1.0',
    'category': 'Warehouse',
    'author': 'Loai Souboh',
    'summary': 'Module for managing two-step internal transfers in Odoo.',
    'description': """
Two-Step Internal Transfer Module
=================================

This module enables you to manage internal transfers using a two-step process.

**Key Features**:
- First operation moves stock from the source location to a transit location.
- Automatically generates a second transfer from the transit location to the final destination.
- Automatically sets the second transfer to "Ready" status.
- Displays second operations under the appropriate destination warehouse.
- Transit location field visibility and mandatory rules are enforced.

**Ideal for**:
- Businesses requiring an intermediate transit point between stock transfers.
- Companies that need to validate stock movements across multiple warehouses.
    """,
    'depends': ['stock'],
    'data': [
        'views/stock_picking_views.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
