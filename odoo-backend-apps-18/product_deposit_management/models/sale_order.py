# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_line_count = fields.Integer("Sale line count")

    @api.onchange('order_line')
    def _onchange_order_line(self):
        if self.sale_line_count - len(self.order_line) == 1:
            self.sale_line_count -= 1
            return {}
        values = []
        # find size attribute_id
        old_line = self.order_line.filtered(lambda sol: sol.product_id.deposit_type == False)

        # iterate thru lines
        for order_line in self.order_line.filtered(
                lambda sol: sol.product_id.deposit_type == 'has_deposit'):
            # add line selected by user
            new_line = order_line.copy_data()[0]
            values.append([0, 0, new_line])
            new_line_values = new_line.copy()
            if order_line.product_packaging_id:
                crate_line_values = order_line.copy_data()[0]
                crate_line_values.update({
                    'price_unit': order_line.product_packaging_id.product_id.lst_price,
                    'product_packaging_qty': False,
                    'product_packaging_id': False,
                    'product_uom_qty': order_line.product_packaging_qty,
                    'product_id': order_line.product_packaging_id.deposit_product_id.id,
                    'name': order_line.product_packaging_id.deposit_product_id.name,
                    'tax_id': [(6, 0, [])]
                })
                values.append([0, 0, crate_line_values])
            if order_line.product_id.deposit_type == 'has_deposit':
                new_line_values.update({
                    'price_unit': order_line.product_id.deposit_product_id.lst_price,
                    'product_packaging_qty': False,
                    'product_packaging_id': False,
                    'product_id': order_line.product_id.deposit_product_id.id,
                    'name': order_line.product_id.deposit_product_id.name,
                    'tax_id': [(6, 0, [])]
                })
            values.append([0, 0, new_line_values])
        if values:
            self.update({'order_line': [(6, 0, [])]})
            self.update({'order_line': values, 'sale_line_count': len(values)})
            self.order_line += old_line
            for order_line in self.order_line:
                order_line._onchange_product_id_warning()
