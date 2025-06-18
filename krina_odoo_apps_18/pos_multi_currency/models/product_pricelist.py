from odoo import models, fields


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    currency_id = fields.Many2one('res.currency', string='Currency')
