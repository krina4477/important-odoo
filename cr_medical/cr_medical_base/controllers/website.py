from odoo.http import Controller, request, route
class WebsiteDemo(Controller):
    @route(['/website-demo'], type='http', auth='public', website=True, csrf=False)
    def website_demo(self, **post):
        patient_id = request.env['res.partner'].search([])
        doctor_id = request.env['res.partner'].search([])
        return request.render("cr_medical_base.website_demo", {'res_data': patient_id,'res1_data': doctor_id})