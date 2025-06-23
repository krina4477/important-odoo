from odoo import models, fields, api


class InheritProductTemplateBarcode(models.Model):
    _inherit = 'product.template.barcode'

    allow_negative_sale_price = fields.Boolean(string='Allow Negative Sale')
