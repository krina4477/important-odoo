from odoo import models, fields, api

class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    is_send_mail = fields.Boolean(string='Send Coupon Code',
                                config_parameter='customer_signup_coupon_cr.is_send_mail')
    signup_program_id = fields.Many2one("loyalty.program", related="company_id.signup_program_id", readonly=False)
