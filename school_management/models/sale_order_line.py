from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def search_by_product_and_user(self, product_id, user_id):
        domain = [('product_id', '=', product_id), ('order_id.partner_id', '=', user_id)]
        order_lines = self.search(domain)
        return order_lines

    @api.constrains('product_id', 'order_id.partner_id')
    def check_duplicate_purchase(self):
        for line in self:
            existing_order_lines = self.search_by_product_and_user(line.product_id.id, line.order_id.partner_id.id)
            if len(existing_order_lines) > 1:
                raise ValidationError("You have already purchased this product before.")
