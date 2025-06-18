from odoo import models, fields


class FeatureLine(models.Model):
    _name = 'feature.line'
    _description = 'Feature Line'

    feature_id = fields.Many2one('feature.feature', string='Feature', required=True)
    feature_value_id = fields.Many2many('feature.value', string='Feature Value', required=True, domain="[('feature_id', '=', feature_id)]")
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    product_id = fields.Many2one('product.product', string='Product Variant')