from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    feature_line_ids = fields.One2many('feature.line', 'product_tmpl_id', string='Feature Lines')