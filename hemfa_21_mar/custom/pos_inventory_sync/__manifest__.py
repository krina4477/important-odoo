{
    'name': 'POS Enhancements for Stock Operations',
    'version': '1.5',
    'category': 'Point of Sale',
    'author': 'Loai Souboh',
    'summary': 'Add POS Config and Session fields to stock operations with filters and group by options.',
    'depends': ['point_of_sale', 'stock'],
    'data': [
        'views/stock_picking_views.xml',
        'views/stock_move_views.xml',
        'views/stock_move_line_search_inherit.xml',
        'views/stock_valuation_layer_search_view.xml',
        'views/stock_valuation_layer_tree_view.xml',
    ],
    'installable': True,
    'application': False,
}
