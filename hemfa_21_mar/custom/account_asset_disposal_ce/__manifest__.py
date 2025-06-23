# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Account Asset Disposal',
    'version': '4.2.1',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'category' : 'Accounting',
    'website': 'https://www.probuse.com',
    'summary' : 'Account Asset Disposal',
    'price' : 149.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'support': 'contact@probuse.com',
    'images': ['static/description/image.jpg'],
     #'live_test_url': 'https://youtu.be/BbgraQzeUIY',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/account_asset_disposal_ce/612',
    'description': '''
Account Asset Disposal
This module enables the feature to dispose the asset. User can use two below methods to dispose any asset.
Sales Dispose
Asset Write-Off
This will allow user to dispose asset of company directly from Asset form. We have provide new tab under Asset form. 
You can see blog of our here on this: http://www.probuse.com/blog/erp-functional-27/post/asset-disposal-write-off-69 
**Note: This module only support Invoice sales of Asset not Cash sales.
asset close
asset dispose
asset disposal
account asset
account asset disposal
disposal process
process disposal

Asset Disposal
Dispose Assets
Account Asset Disposal,

  ''',
    'depends':[
        'odoo_account_asset',
    ],
    'data' : [
        'views/asset_view.xml',
    ],
    'installable':True,
    'auto_install':False
}

