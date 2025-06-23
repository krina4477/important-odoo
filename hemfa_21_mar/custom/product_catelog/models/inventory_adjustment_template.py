# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from datetime import timedelta
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from odoo.tools.sql import create_index

from odoo.addons.payment import utils as payment_utils


class InventoryAdjustment(models.Model):
    _name = 'inventory.adjustment.template.new'
    _inherit = ['inventory.adjustment.template.new', 'product.catalog.mixin']
    _description = "Inventory Adjustment Template New"



    def _update_order_line_globle_click(self, product_id, quantity, **kwargs):
        """ Update sale order line information for a given product or create a
        new one if none exists yet.
        :param int product_id: The product, as a `product.product` id.
        :return: The unit price of the product, based on the pricelist of the
                 sale order and the quantity selected.
        :rtype: float
        """
        inventory_adjustment = self.adjst_line_ids.filtered(lambda line: line.product_id_new.id == product_id)
        if inventory_adjustment:
            if quantity != 0:
                inventory_adjustment.counted_qty = quantity
            else:
                inventory_adjustment.counted_qty = 0
        elif quantity > 0:
            inventory_adjustment = self.env['inventory.adjustment.template.new.line'].create({
                'inventory_id': self.id,
                'product_id_new': product_id,
                'counted_qty': quantity,
                # put it at the end of the order
            })
        return inventory_adjustment

    def _update_order_line_info(self, product_id, quantity, barcode_cutom, **kwargs):

        inventory_adjustment = self.adjst_line_ids
        inventory_adjustment_line = inventory_adjustment.filtered(lambda line: line.product_barcode == str(barcode_cutom))

        if inventory_adjustment_line:
            inventory_adjustment_line.counted_qty += 1
            return inventory_adjustment_line
        else:
            dynamic_barcode = self.env['product.template.barcode'].search([('name', '=', str(barcode_cutom))])
            if dynamic_barcode:
                inventory_adjustment_line =  inventory_adjustment.filtered(lambda line: line.product_barcode == str(barcode_cutom))
                if inventory_adjustment_line:
                    inventory_adjustment_line.counted_qty += 1
                    return inventory_adjustment_line
                else:
                    inventory_adjustment = self.env['inventory.adjustment.template.new.line'].create({
                        'inventory_id': self.id,
                        'product_id_new': product_id,
                        'counted_qty': 1,
                        'product_uom': dynamic_barcode.unit.id,
                        'product_barcode': barcode_cutom,
                    })
                    return inventory_adjustment
            else:
                if inventory_adjustment_line:
                    inventory_adjustment_line = inventory_adjustment_line.filtered(lambda line: not line.product_barcode)
                    if inventory_adjustment_line:
                        inventory_adjustment_line[0].counted_qty += 1
                        return inventory_adjustment_line[0]
                    else:
                        inventory_adjustment_line = self.env['inventory.adjustment.template.new.line'].create({
                            'inventory_id': self.id,
                            'product_id_new': product_id,
                            'counted_qty': 1,
                            # put it at the end of the order
                        })
                        return inventory_adjustment_line
                else:
                    inventory_adjustment_line = self.env['inventory.adjustment.template.new.line'].create({
                        'inventory_id': self.id,
                        'product_id_new': product_id,
                        'counted_qty': 1,
                        # put it at the end of the order
                    })
                return inventory_adjustment_line

    def _default_order_line_values(self):
        default_data = super()._default_order_line_values()
        new_default_data = self.env['inventory.adjustment.template.new.line']._get_product_catalog_lines_data()
        return {**default_data, **new_default_data}

    def _get_action_add_from_catalog_extra_context(self):
        return {
            **super()._get_action_add_from_catalog_extra_context(),
            # 'product_catalog_currency_id': self.currency_id.id,
            # 'product_catalog_digits': self.order_line._fields['price_unit'].get_digits(self.env),
        }

    def _get_product_catalog_domain(self):
        pass
        # return expression.AND([super()._get_product_catalog_domain(), [('purchase_ok', '=', True)]])

    def _get_product_catalog_record_lines(self, product_ids):
        grouped_lines = defaultdict(lambda: self.env['inventory.adjustment.template.new.line'])
        for line in self.adjst_line_ids:
            if line.product_id_new.id not in product_ids:
                continue
            grouped_lines[line.product_id_new] |= line
        return grouped_lines

class InventoryAdjustmentLine(models.Model):
    _inherit = 'inventory.adjustment.template.new.line'

    product_uom = fields.Many2one('uom.uom',string='Unit of Measure')

    def _get_product_catalog_lines_data(self, **kwargs):
        """ Return information about sale order lines in `self`.

        If `self` is empty, this method returns only the default value(s) needed for the product
        catalog. In this case, the quantity that equals 0.

        Otherwise, it returns a quantity and a price based on the product of the SOL(s) and whether
        the product is read-only or not.

        A product is considered read-only if the order is considered read-only (see
        ``SaleOrder._is_readonly`` for more details) or if `self` contains multiple records
        or if it has sale_line_warn == "block".

        Note: This method cannot be called with multiple records that have different products linked.

        :raise odoo.exceptions.ValueError: ``len(self.product_id) != 1``
        :rtype: dict
        :return: A dict with the following structure:
            {
                'quantity': float,
                'price': float,
                'readOnly': bool,
                'warning': String
            }
        """
        if len(self) == 1:
            res = {
                'quantity': self.counted_qty,
                'price': 0,
                'readOnly': self.inventory_id._is_readonly() or (self.product_id_new.sale_line_warn == "block"),
            }
            if self.product_id_new.sale_line_warn != 'no-message' and self.product_id_new.sale_line_warn_msg:
                res['warning'] = self.product_id_new.sale_line_warn_msg
            return res
        elif self:
            self.product_id_new.ensure_one()
            order_line = self[0]
            order = order_line.inventory_id
            res = {
                'readOnly': False,
                'price': 0,
                'quantity': sum(self.mapped(lambda line: line.counted_qty))
            }
            if self.product_id_new.sale_line_warn != 'no-message' and self.product_id_new.sale_line_warn_msg:
                res['warning'] = self.product_id_new.sale_line_warn_msg
            return res
        else:
            return {
                'quantity': 0,
                'price': 0,
                # price will be computed in batch with pricelist utils so not given here
            }