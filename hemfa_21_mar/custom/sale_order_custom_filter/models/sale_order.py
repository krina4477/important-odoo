from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_type = fields.Selection([
        ('all', 'All'),
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product')
    ], string="Product Type", default='all')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_template_id')
    def _onchange_product_type(self):
        if self.order_id:
            product_type = self.order_id.product_type
            print(f"Product Type Selected: {product_type}")  # Debugging line

            if product_type == 'all':
                domain = []
            elif product_type:
                domain = [('detailed_type', '=', product_type)]
            else:
                domain = []

            print(f"Domain Applied: {domain}")  # Debugging print

            return {
                'domain': {
                    'product_id': domain,
                    'product_template_id': domain
                }
            }
