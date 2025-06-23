# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Sale Confirmation backdate',
    'version': '14.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Sales Management',
    'description':
        """
 odoo Module add below functionality into odoo

        1.Pass Confirmation date manually while confirming sale order\n
        
        sale confirm date 
        sale confirm past date  
        sale confirm date
        sale order Confirmation Date
Odoo Sale Confirmation Date
Manage Sale Confirmation Date
Odoo manage Sale Confirmation Date
Pass/set Confirmation date manually while confirming sale order
Odoo Pass/set Confirmation date manually while confirming sale order
Pass Confirmation date manually while confirming sale order
Odoo Pass Confirmation date manually while confirming sale order
Set Confirmation date manually while confirming sale order
Odoo Set Confirmation date manually while confirming sale order
Sale Order confirmation date 
Odoo sale order confirmation date 
Manage sale order confirmation date 
Odoo manage sale order confirmation date 
Confirm sale order 
Odoo confirm sale order 
Pass sale confirmation date manually 
Odoo pass confirmation date manually 
Set sale confirmation date manually 
Odoo set sale confirmation date manually 

    """,
    'summary': 'odoo app pass confirmation date manually while confirming sale order | Sale confirm date | sale confirm past date  | backdate | Sale confirm backdate | Sale backdate | Sale Pastdate | sale confirm past date   | sale old date | confirmation date  | pastdate | backdate sale | sale date process',
    'depends': ['sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/dev_sale_confirm_view.xml',
        'views/sale_order_view.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':11.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
