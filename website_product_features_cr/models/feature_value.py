from odoo import models, fields


class FeatureValue(models.Model):
    _name = 'feature.value'
    _description = 'Feature Value'

    name = fields.Char(required=True)
    feature_id = fields.Many2one('feature.feature', string='Feature', required=True)