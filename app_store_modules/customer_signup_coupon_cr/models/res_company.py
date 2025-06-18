from odoo import models,api,fields,_


class ResCompany(models.Model):
    _inherit = 'res.company'

    signup_program_id = fields.Many2one("loyalty.program", "Signup Program", domain = [('program_type', '=', 'coupons')])