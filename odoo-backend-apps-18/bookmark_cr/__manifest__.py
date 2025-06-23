# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Bookmark Records",
    'version': '18.0.0.1',
    'summary': """
        Allow user to bookmark any record 
    """,
    'description': """
    
    This module has following features.

   * allow user to bookmark any record
   * allow user to remove bookmark
   * allow user to access own bookmarks
   * allow user to open and view bookmark record
   * remove multiple bookmark from list view

    """,

    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://candidroot.com/",
    'images' : ['static/description/banner.png'],
    'category': 'Tools',
    'depends': ['web','sale', 'mail', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/bookmark.xml',
    ],
    'demo': [],
    'license':'LGPL-3',
    'live_test_url': 'https://youtu.be/xLo9rSuPNVM',
    'price': 9.99,
    'currency': 'USD',
    'assets':{
        'web.assets_backend': [
            'bookmark_cr/static/src/lib/jquery.min.js',
            'bookmark_cr/static/src/js/bookmark.js',
            'bookmark_cr/static/src/js/inherit_form_controller.js',
            'bookmark_cr/static/src/js/inherit_list_controller.js',
            'bookmark_cr/static/src/xml/bookmark_button.xml'

            # 'bookmark_cr/static/src/**/*',
        ],
    }
}