# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api
from collections import defaultdict

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_line_count = fields.Integer("Purchase line count")

    @api.model_create_multi
    def create(self, vals_list):
        # Create purchase orders
        purchase_orders = super(PurchaseOrder, self).create(vals_list)

        for purchase_order in purchase_orders:
            # Trigger custom logic to process order lines
            purchase_order._apply_order_line_sequence()

        return purchase_orders

    def _apply_order_line_sequence(self):
        """Process order lines to set the sequence field and ensure deposit products appear after main products."""
        self.ensure_one()

        product_lines = []
        deposit_lines = []
        merged_dict = defaultdict(lambda: None)

        # Store data of old lines instead of record references
        old_line_data = [line.copy_data()[0] for line in
                         self.order_line.filtered(lambda pol: not pol.product_id.deposit_type)]

        for order_line in self.order_line.filtered(lambda pol: pol.product_id.deposit_type == 'has_deposit'):
            product_lines.append([0, 0, order_line.copy_data()[0]])

            if order_line.product_packaging_id and order_line.product_packaging_id.deposit_product_id:
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
                deposit_lines.append([0, 0, crate_line_values])

            if order_line.product_id.deposit_product_id:
                deposit_line_values = order_line.copy_data()[0]
                deposit_line_values.update({
                    'price_unit': order_line.product_id.deposit_product_id.lst_price,
                    'product_packaging_qty': False,
                    'product_packaging_id': False,
                    'product_qty': order_line.product_qty,
                    'product_id': order_line.product_id.deposit_product_id.id,
                    'name': order_line.product_id.deposit_product_id.name,
                    'taxes_id': [(6, 0, [])]
                })
                deposit_lines.append([0, 0, deposit_line_values])

        combined_lines = product_lines + deposit_lines
        for record in combined_lines:
            _, _, details = record
            product_id = details['product_id']
            if product_id in merged_dict:
                merged_dict[product_id]['product_qty'] += details['product_qty']
            else:
                merged_dict[product_id] = details.copy()

        merged_data = [[0, 0, details] for details in merged_dict.values()]

        if merged_data:
            # Clear existing order lines
            self.update({'order_line': [(6, 0, [])]})
            self.update({'order_line': merged_data})

            # Reattach old lines using copied data
            self.update({'order_line': [(0, 0, data) for data in old_line_data]})

        # Ensure correct sequence order
        main_products = []
        deposit_products = []
        for line in self.order_line:
            if not line.product_id.deposit_product_id:
                main_products.append(line)  # Main products
            else:
                deposit_products.append(line)  # Deposit products

        sorted_lines = main_products + deposit_products
        # Apply sorted sequence
        for index, line in enumerate(sorted_lines, start=1):
            line.sequence = index

    @api.onchange('order_line')
    def _onchange_order_line(self):
        self._apply_order_line_sequence()