# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_line_count = fields.Integer("Purchase line count")

    @api.onchange('order_line')
    def _onchange_order_line(self):
        ''' generated automated lines for deposit products on onchange instead of create/write, so user can see on
        selection of product.'''
        if self.purchase_line_count - len(self.order_line) == 1:
            self.purchase_line_count -= 1
            return {}
        values = []

        # find lines for non-related product (deposit type not configured)
        old_line = self.order_line.filtered(lambda pol: pol.product_id.deposit_type == False)

        # iterate thru lines
        for order_line in self.order_line.filtered(
                lambda pol: pol.product_id.deposit_type == 'has_deposit'):
            # add line for bottle product deposit
            new_line = order_line.copy_data({'price_unit': order_line.product_id.lst_price})[0]
            values.append([0, 0, new_line])
            new_line_values = new_line.copy()
            # add line for crate product deposit if packaging is defined
            if order_line.product_packaging_id:
                crate_line_values = order_line.copy_data()[0]
                crate_line_values.update({
                    'price_unit': order_line.product_packaging_id.deposit_product_id.lst_price,
                    'product_packaging_qty': False,
                    'product_packaging_id': False,
                    'product_qty': order_line.product_packaging_qty,
                    'product_id': order_line.product_packaging_id.deposit_product_id.id,
                    'name': order_line.product_packaging_id.deposit_product_id.name,
                    'taxes_id': [(6, 0, [])]
                })
                values.append([0, 0, crate_line_values])
            if order_line.product_id.deposit_type == 'has_deposit':
                new_line_values.update({
                    'price_unit': order_line.product_id.deposit_product_id.lst_price,
                    'product_packaging_qty': False,
                    'product_packaging_id': False,
                    'product_qty': order_line.product_qty,
                    'product_id': order_line.product_id.deposit_product_id.id or False,
                    'name': order_line.product_id.deposit_product_id.name,
                    'taxes_id': [(6, 0, [])]
                })
                values.append([0, 0, new_line_values])

        if values:
            self.update({'order_line': [(6, 0, [])]})
            self.update({'order_line': values, 'purchase_line_count': len(values)})
            self.order_line += old_line
            # for order in self.order_line:
            #     order._product_id_change()
