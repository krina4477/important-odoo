from odoo import models, fields

class Product3DImage(models.Model):
    _name = 'product.3d.image'
    _description = '3D Product Image'

    name = fields.Char(string="Name")
    prod_3d_img = fields.Binary(string="3D File")
    prod_3d_img_filename = fields.Char(string="File Name")
    product_id = fields.Many2one('product.product', string="Product")



# from odoo import fields, models



# class ProductImage(models.Model):
#     _inherit = 'product.image'

#     prod_3d_img = fields.Binary('Product 3D Image')
#     product_templ_id = fields.Many2one('product.product','Product Template')




