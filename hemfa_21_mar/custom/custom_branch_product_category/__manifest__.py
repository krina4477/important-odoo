{
    'name': 'Branch-Based Product Categories',
    'version': '16.0.1.5',
    'summary': 'Manage product categories visibility by branch.',
    'description': """
Branch-Based Product Categories
================================

This module extends the product category functionality by adding a branch field to categorize products based on branch visibility. 

**Features:**
- Assign product categories to specific branches.
- Restrict visibility of product categories based on user branch assignments.
- Allow categories to be visible to all branches if no specific branch is assigned.
- Update product category views with branch-specific filtering.

This app ensures better product management in multi-branch setups.
""",
    'author': 'Loai Souboh',
    'website': 'https://yourwebsite.com',
    'depends': ['product', 'base', 'branch'],
    'data': [
        'security/ir.model.access.csv',
        'security/product_category_rules.xml',
        'views/product_category_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
