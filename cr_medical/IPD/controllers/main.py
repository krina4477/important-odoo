from odoo.http import Controller, request, route


class WebsiteDemo(Controller):
    @route(['/website-demo'], type='http', auth='user', website=True)
    def website_demo_view(self, **post):
        res_data = request.env['res.partner'].sudo().search([('is_patient', '=', True)])
        return request.render("cr_medical_base.website_demo", {'res_data': res_data})

    @route(['/website-demo-test'], type='http', auth='public', website=True, csrf=False)
    def website_demo_save(self, **post):
        temp = request.env['res.partner'].sudo().create({
            'name': post.get('fname'),
            'date_of_birth': post.get('birthday'),
            'sex': 'male',
            'blood_group': 'A+',
            'mobile': post.get('number'),
            'is_patient': True
        })
        return request.redirect('/contactus-thank-you')
