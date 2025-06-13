from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'


    product_3d_image_ids = fields.One2many('product.3d.image', 'product_id', string="3D Media")
