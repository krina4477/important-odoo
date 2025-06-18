{
    'name': 'POS Multi Currency Pricelist',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Allows multiple currencies in POS price lists',
    'depends': ['point_of_sale', 'account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_config_views.xml',
        # 'views/product_pricelist_views.xml',
        # 'data/pos_data.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_multi_currency/static/src/js/pos_currency.js',
        ],
    },
    'installable': True,
    'application': False,
}