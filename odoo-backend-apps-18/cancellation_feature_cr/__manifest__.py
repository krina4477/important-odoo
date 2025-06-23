# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Cancellation Order Feature",
    'category': 'Sales/Sales',
    'summary': """ Cancellation Feature for Sales Order, Purchase Order, Inventory and Invoice.""",
    'version': '18.0.0.0',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'sequence': 2,
    'description': """ This module will help you to do the following things in simple way.
    
   --- You need to configure the options available in Sales/Configuration/Settings and Purchase/Configuration/Setting ---. 
   
Sale
------------------------
> You can cancel a Sale order, once it is confirmed.
> After cancellation of order, product quantity will be reverted in inventory.
   NOTE --> ( If you enabled the [Cancel Delivery Order] option in Sale's configuration then the quantity will be affected,
              otherwise only Sale order will be cancelled.)  
> You can cancel multiple Sale orders in one click.
> You can cancel sale's invoice
   NOTE --> ( If you enabled the [Cancel Invoice and Payment] option in Sale configuration then invoice
               will be cancelled.)  

Purchase
------------------------
> You can cancel a Purchase order, once it is confirmed.
> After cancellation of order, product quantity will be revert in inventory.
   NOTE --> ( If you checked [Cancel Receipt Order] option in Purchase configuration then the quantity will be affected,
              otherwise only Purchase order will cancel.)  
> You can cancel multiple Purchase orders in one click.
> You can cancel Purchase's invoice
   NOTE --> ( If you checked [Cancel Bill] option in Purchase's configuration then invoice
              will cancel.)
 
Inventory
------------------------
> You can cancel Delivery order, Receipt and Internal Transfer which are in done state only.
> NOTE --> ( If you checked [Stock Picking Cancel Operation Type] option in Inventory configuration
              then it will be cancelled.)
> You can cancel multiple Delivery order, Receipt and Internal Transfer in one click.
> You can cancel multiple Stock moves.
> NOTE --> You can find stock move from (Inventory > Reporting > Stock Moves)   
 
Invoice
------------------------
> You can cancel Invoice/Bill  which are in Posted state.
> If you cancel a Invoice/Bill then corresponding payment will also be cancelled if payment is in posted state.
> You can also cancel Payment which are already Posted.
 
         """,
    'depends': ["base", "sale_stock", "account", "sale_management", "sale", "purchase"],
    'data': [
        'security/security.xml',
        'data/ir_actions_server.xml',
        'views/stock_view.xml',
        'views/invoice_view.xml',
        'views/sale_settings_view.xml',
        'views/purchase_settings_view.xml',
        'views/inventory_settings_view.xml',
        'views/invoice_settings_view.xml',
    ],
    'qweb': [],
    'images': ['static/description/banner.jpeg'],
    'installable': True,
    'live_test_url': 'https://youtu.be/Ibq81e7GRSQ',
    'price': 79.99,
    'currency': 'USD',
    'auto_install': False,
    'application': False,
}
