from odoo import models, fields, api


class LoyaltyCard(models.Model):
    _inherit = 'loyalty.card'

    is_show_coupon_details = fields.Boolean(string='Is Show Coupon Details')