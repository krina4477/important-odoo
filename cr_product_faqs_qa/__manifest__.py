# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.



{
    'name': "Product FAQs and Q&A",
    'summary': """Add customer-friendly FAQs and Q&A functionality to product pages on your Odoo website.""",
    'description': """This module enables a Q&A and FAQ system for products on the Odoo website. It allows customers to ask questions directly from the product page, and admins or sellers or user can respond publicly. The module also supports predefined Frequently Asked Questions (FAQs), improving customer experience and reducing support inquiries.""",
    'author': 'Candidroot Solutions Pvt. Ltd',
    'category': 'Extra Tools',
    'version': '18.0.0.1',
    'depends': ['sale_management','website_sale'],
    'data': [
        'security/ir.model.access.csv',
        
        'views/question_answer_view.xml',
        'views/product_template.xml',
        
        'templates/product_page.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'cr_product_faqs_qa/static/src/js/product_page.js',
        ]
    },
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
    'website': 'https://www.candidroot.com/'
}


