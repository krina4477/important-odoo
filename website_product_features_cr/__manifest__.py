{
    'name': 'Website Product Features',
    'version': '18.0.0.1',

    'description': """
        Product Features
    """,
    'author': 'Candidroot Pvt.Ltd.',
    'website': 'https://www.candidroot.com/',
    'depends': [
        'website_sale', 'website', 'stock', 'product'
    ],
    'category': 'Website',
    'assets': {
    'web.assets_frontend': [
            'website_product_features_cr/static/src/js/product_features.js',
            'website_product_features_cr/static/src/css/product_features.css',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/feature_value.xml',
        'views/feature_views.xml',
        'views/product_features.xml',
        'views/product_product.xml',
        'views/product_template.xml',
    ],
    'installable': True,
    'price': 19.99,
    'currency': 'USD',
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
