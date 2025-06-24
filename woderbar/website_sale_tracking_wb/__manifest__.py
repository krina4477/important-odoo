# Copyright © 2024 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)

{
    'name': 'eCommerce Tracking customizations for Wunderbar',
    'version': '15.0.1.1.0',
    'category': 'eCommerce',
    'author': 'Garazd Creation',
    'website': 'https://garazd.biz',
    'license': 'OPL-1',
    'summary': 'eCommerce Tracking customizations for Wunderbar',
    'depends': [
        'website_ecom_custom',
    ],
    'data': [
        'views/website_sale_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_sale_tracking_wb/static/src/js/website_sale_tracking.js',
        ],
    },
    'price': 100.0,
    'currency': 'EUR',
    'support': 'support@garazd.biz',
    'application': False,
    'installable': True,
    'auto_install': False,
}
