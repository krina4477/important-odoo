# -*- coding: utf-8 -*-

{
    'name': 'Website Signup reCAPTCHA',
    'version': '18.0.1.0.1',
    'summary': """Protect your website signup form from bots using Google reCAPTCHA.""",
    'description': """Secure your website's user registration process by integrating Google reCAPTCHA into the signup form.
                    Key Features:
                    - Adds Google reCAPTCHA to the website signup page.
                    - Blocks automated bot signups and reduces spam user creation.
                    - Easy configuration via Website Settings.
                    - Requires a Google reCAPTCHA site key and secret key (provided by Google).
                    - Supports v2 reCAPTCHA (checkbox).""",
    'author': 'Candidroot Solutions Pvt Ltd',
    'company': 'Candidroot Solutions Pvt Ltd',
    'website': 'https://www.candidroot.com',
    'category': 'Website',
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'depends': ['base','website'],
    'data': [
            'views/captcha_views.xml',
            'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'google_signup_recaptcha_cr/static/src/js/signup.js',
        ],
    },
    'installable': True,
    'price': 20,
    'currency': 'USD',
    'auto_install': False,
    'application': True,

}
