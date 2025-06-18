from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    feature_line_ids = fields.One2many('feature.line', 'product_id', string='Feature Lines')