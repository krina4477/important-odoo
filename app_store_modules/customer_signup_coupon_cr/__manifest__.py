{
    'name': 'Customer Signup Coupon Code',
    'version': '18.0.0.1',
    'description': """
        This module automatically sends a coupon code to users via email when they sign up to your Odoo website.
        It is useful for marketing, promotions, and customer retention by rewarding users with discount codes.
        The module integrates with Odoo Website Sale and Loyalty modules.
    """,
    'category': 'Ecommerce',
    'author': 'Candidroot Pvt.Ltd.',
    'website': 'https://www.candidroot.com/',
    'depends': [
        'website_sale', 'website', 'sale_loyalty', 'loyalty', 
        'sale_loyalty_delivery', 'sale_management', 'base', 'website_sale_loyalty',
    ],
    'data': [
        'views/res_config_setting.xml',
        'views/inherit_loyalty_card.xml',
        'views/inherit_showable_rewards.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
