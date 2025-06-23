# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.
{
    "name": "CN DN Customisation",
    "version": "16.0.29",
    "summary": "CN DN Customisation",
    "description": """
        - This module add the following functionality for CN/DN number customisation for stock operations.
        - while confirming the purchase reciept it will generat the DN number for incomming pickings.
    """,
    "category": 'Customization',

    # Author
    "author": "Bahelim Munafkhan",
    "website": "https://www.4minds.com",
    "license": "LGPL-3",

    # Dependency
    "depends": [
        'stock', 'sale_stock', 'purchase_stock', 'sale_management',
        'Two_Step_Internal_Transfer', 'hemfa_warehouse_stock_request',
        'point_of_sale', 'sh_pos_all_in_one_retail', 'product_catelog'],

    "data": [
        "security/stock_security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        # "views/stock_backorder_confirmation_views.xml",
        "views/tracking_number_views.xml",
        "views/stock_move_line_views.xml",
        'views/stock_quant_views.xml',
        "views/stock_picking_return_view.xml",
        'wizards/transfer_whole_dn_views.xml',
        'wizards/product_barcode.xml',
        'report/dn_cn_report_action.xml',
        'report/dn_cn_report_views.xml',
        'report/transfer_report.xml',
    ],

    "installable": True,
    "application": False,
    "auto_install": False
}
