{
    'name': 'Product Catelog',
    'version': '16.0.0.11',
    'summary': 'Product Catelog',
    'description': """Product Catelog""",
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://candidroot.com/",
    'depends': ['web', 'sale', 'sale_management', 'product','purchase','account','stock'],
    "data": [
         'views/product.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'product_catelog/static/src/product_catalog/**/*.js',
            'product_catelog/static/src/product_catalog/**/*.xml',
            'product_catelog/static/src/product_catalog/**/*.scss',
        ],
    },
    'installable': True,
    'auto_install': False,  
    'application': False,
}
