# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': "Blog Post URL Redirect URL Rewrite",
    'summary': "SEO URL Redirect, Blog Post URL Rewrite",
    'description': "This module allows user to redirect the blog url to the configured url.",
    'category': 'Website Blog',
    'version': '18.0.0.0',
    'depends': ['base','website_blog'],
    'author': 'Candidroot Solutions Pvt. Ltd.',
    'website': 'https://www.candidroot.com',
    'data': [
        'security/ir.model.access.csv',
        'views/website_url_redirect_rewrite_view.xml',
        'views/blog_post_view.xml',
    ],
    'demo': [
    ],
    'images' : ['static/description/banner.jpeg'],
    'price': 49.99,
    'currency': 'EUR',
    'live_test_url': 'https://youtu.be/z9EK6Ihuc8g',
    'installable': True,
    'license': 'OPL-1',
    'external_dependencies': {'python': ['qrcode', 'pyotp']},
}