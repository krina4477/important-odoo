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


class CustomWarehouse(models.Model):
    _name = 'custom.warehouse.stock.request'
    _inherit = ['custom.warehouse.stock.request', 'product.catalog.mixin']
    _description = "Custom Warehouse Stock Request"

    def _update_order_line_globle_click(self, product_id, quantity, **kwargs):
        """ Update sale order line information for a given product or create a
        new one if none exists yet.
        :param int product_id: The product, as a `product.product` id.
        :return: The unit price of the product, based on the pricelist of the
                 sale order and the quantity selected.
        :rtype: float
        """
        warehouse_stock_line = self.warehouse_stock_request_line_ids.filtered(
            lambda line: line.product_id.id == product_id)
        if warehouse_stock_line:
            if quantity != 0:
                warehouse_stock_line.demand_qty = quantity
            elif self.state in ['draft', 'sent']:
                warehouse_stock_line.unlink()
                return warehouse_stock_line
            else:
                warehouse_stock_line.demand_qty = 0
        elif quantity > 0:
            product_description = self.env['product.product'].browse(product_id)
            warehouse_stock_line = self.env['custom.warehouse.stock.request.line'].create({
                'stock_request_id': self.id,
                'product_id': product_id,
                'demand_qty': quantity,
                'description': product_description.name,
                'product_uom': product_description.uom_id.id,
                # 'sequence': ((self.warehouse_stock_request_line_ids and self.warehouse_stock_request_line_ids[
                #     -1].sequence + 1) or 10),
                # put it at the end of the order
            })
        return warehouse_stock_line

    def _update_order_line_info(self, product_id, quantity, barcode_cutom, **kwargs):
        print("==============================22=2=2=2=2=2=22==2=2")
        warehouse_stock_line = self.warehouse_stock_request_line_ids
        warehouse_stock_line_line = warehouse_stock_line.filtered(lambda line: line.product_barcode == str(barcode_cutom))
        product_description = self.env['product.product'].browse(product_id)

        if warehouse_stock_line_line:
            warehouse_stock_line_line.demand_qty += 1
            return warehouse_stock_line_line
        else:
            dynamic_barcode = self.env['product.template.barcode'].search([('name', '=', str(barcode_cutom))])
            if dynamic_barcode:
                warehouse_stock_line_line = warehouse_stock_line.filtered(lambda line: line.product_barcode == str(barcode_cutom))
                if warehouse_stock_line_line:
                    warehouse_stock_line_line.demand_qty += 1
                    return warehouse_stock_line_line
                else:
                    warehouse_stock_line = self.env['custom.warehouse.stock.request.line'].create({
                        'stock_request_id': self.id,
                        'product_id': product_id,
                        'demand_qty': 1,
                        # 'sequence': ((self.warehouse_stock_request_line_ids and self.warehouse_stock_request_line_ids[-1].sequence + 1) or 10),
                        'product_uom': dynamic_barcode.unit.id,
                        'product_barcode': barcode_cutom,
                        'description': product_description.name
                    })
                    return warehouse_stock_line
            else:
                if warehouse_stock_line:
                    warehouse_stock_line = warehouse_stock_line.filtered(lambda line: not line.product_barcode)
                    if warehouse_stock_line:
                        warehouse_stock_line[0].demand_qty += 1
                        return warehouse_stock_line[0]
                    else:
                        warehouse_stock_line = self.env['custom.warehouse.stock.request.line'].create({
                            'stock_request_id': self.id,
                            'product_id': product_id,
                            'demand_qty': 1,
                            'description': product_description.name,
                            'product_uom': product_description.uom_id.id,
                            # 'sequence': ((self.warehouse_stock_request_line_ids and self.warehouse_stock_request_line_ids[-1].sequence + 1) or 10),
                            # put it at the end of the order
                        })
                        return warehouse_stock_line
                else:
                    warehouse_stock_line = self.env['custom.warehouse.stock.request.line'].create({
                        'order_id': self.id,
                        'product_id': product_id,
                        'demand_qty': 1,
                        'description': product_description.name,
                        'product_uom': product_description.uom_id.id,
                        # 'sequence': ((self.warehouse_stock_request_line_ids and self.warehouse_stock_request_line_ids[-1].sequence + 1) or 10),
                        # put it at the end of the order
                    })
                return warehouse_stock_line

    def _default_order_line_values(self):
        default_data = super()._default_order_line_values()
        new_default_data = self.env['custom.warehouse.stock.request.line']._get_product_catalog_lines_data()
        return {**default_data, **new_default_data}

    def _get_action_add_from_catalog_extra_context(self):
        return {
            **super()._get_action_add_from_catalog_extra_context(),
            # 'product_catalog_currency_id': self.currency_id.id,
            # 'product_catalog_digits': self.order_line._fields['price_unit'].get_digits(self.env),
        }

    def _get_product_catalog_domain(self):
        # return expression.AND([super()._get_product_catalog_domain(), [('sale_ok', '=', True)]])
        pass

    def _get_product_catalog_record_lines(self, product_ids):
        grouped_lines = defaultdict(lambda: self.env['custom.warehouse.stock.request.line'])
        for line in self.warehouse_stock_request_line_ids:
            if line.product_id.id not in product_ids:
                continue
            grouped_lines[line.product_id] |= line
        return grouped_lines


class CustomWarehouseLine(models.Model):
    _inherit = 'custom.warehouse.stock.request.line'


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
                'quantity': self.demand_qty,
                'price': 0,
                'readOnly': self.stock_request_id._is_readonly() or (self.product_id.sale_line_warn == "block"),
            }
            if self.product_id.sale_line_warn != 'no-message' and self.product_id.sale_line_warn_msg:
                res['warning'] = self.product_id.sale_line_warn_msg
            return res
        elif self:
            self.product_id.ensure_one()
            order_line = self[0]
            order = order_line.stock_request_id
            res = {
                'readOnly': False,
                'price': 0,
                'quantity': sum(
                    self.mapped(
                        lambda line: line.demand_qty
                    )
                )
            }
            if self.product_id.sale_line_warn != 'no-message' and self.product_id.sale_line_warn_msg:
                res['warning'] = self.product_id.sale_line_warn_msg
            return res
        else:
            return {
                'quantity': 0,
                'price': 0,
                # price will be computed in batch with pricelist utils so not given here
            }
