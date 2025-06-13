from odoo import models, fields


class Feature(models.Model):
    _name = 'feature.feature'
    _description = 'Product Feature'

    name = fields.Char(required=True)
    value_ids = fields.One2many('feature.value', 'feature_id', string='Values')
