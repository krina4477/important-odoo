
from odoo import http
from odoo.http import request
import json
import requests
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

class AuthSignupIhn(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):                  
        if request.httprequest.method == 'POST' and request.env['res.config.settings'].sudo().get_values().get('show_captcha'):    
            if kw.get('g-recaptcha-response'):                
                client_key = kw['g-recaptcha-response']
                secret_key = request.env['res.config.settings'].sudo().get_values().get('captcha_private_key')
                captcha_data = {
                    'secret': secret_key,
                    'response': client_key
                }
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=captcha_data)            
                response = json.loads(r.text)            
                verify = response['success']                    
                if verify:                                                         
                    return super(AuthSignupIhn, self).web_auth_signup(*args, **kw)
                else:                    
                    return False
            else:                
                return False
        else:
            return super(AuthSignupIhn, self).web_auth_signup(*args, **kw)