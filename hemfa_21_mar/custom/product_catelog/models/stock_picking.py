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


class Stockpicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'product.catalog.mixin']
    _description = "stock picking"

    def _update_order_line_globle_click(self, product_id, quantity, **kwargs):
        """ Update sale order line information for a given product or create a
        new one if none exists yet.
        :param int product_id: The product, as a `product.product` id.
        :return: The unit price of the product, based on the pricelist of the
                 sale order and the quantity selected.
        :rtype: float
        """
        spl = self.move_ids_without_package.filtered(lambda line: line.product_id.id == product_id)
        if spl:
            if quantity != 0:
                spl.product_uom_qty = quantity
            # elif self.state in ['draft', 'sent']:
            # price_unit = self.pricelist_id._get_product_price(
            #     product=sol.product_id,
            #     quantity=1.0,
            #     currency=self.currency_id,
            #     date=self.date_order,
            #     **kwargs,
            # )
            # sol.unlink()
            # return price_unit
            else:
                spl.product_uom_qty = 0
        elif quantity > 0:
            spl = self.env['stock.move'].create({
                'name': self.name,
                'picking_id': self.id,
                'product_id': product_id,
                'product_uom_qty': quantity,
                'picking_type_id': self.picking_type_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                # 'sequence': ((self.order_line and self.order_line[-1].sequence + 1) or 10),
                # put it at the end of the order
            })
        return spl

    def _update_order_line_info(self, product_id, quantity, barcode_cutom, **kwargs):
        """ Update sale order line information for a given product or create a
        new one if none exists yet.
        :param int product_id: The product, as a `product.product` id.
        :return: The unit price of the product, based on the pricelist of the
                 sale order and the quantity selected.
        :rtype: float
        """
        """ Update sale order line information for a given product or create a
        new one if none exists yet.
        :param int product_id: The product, as a `product.product` id.
        :return: The unit price of the product, based on the pricelist of the
                 sale order and the quantity selected.
        :rtype: float
        """
        spl = self.move_ids_without_package
        spl_line = spl.filtered(lambda line: line.product_barcode == str(barcode_cutom))
        print("===================3-3-3-2-2-3-2-32-3-2-32-0", product_id, barcode_cutom)
        if spl_line:
            spl_line[0].product_uom_qty += 1
            return True
        else:
            dynamic_barcode = self.env['product.template.barcode'].search([('name', '=', str(barcode_cutom))], limit=1)
            if dynamic_barcode:
                if spl_line:
                    spl_line[0].product_uom_qty += 1
                    return True
                else:
                    spl = self.env['stock.move'].create({
                        'name': self.name,
                        'picking_id': self.id,
                        'product_id': dynamic_barcode.product_id.id,
                        'product_uom_qty': 1,
                        # 'sequence': ((self.order_line and self.order_line[-1].sequence + 1) or 10),
                        'product_uom': dynamic_barcode.unit.id,
                        'product_barcode': barcode_cutom,
                        'picking_type_id': self.picking_type_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                    })
                    return True
            else:
                if spl:
                    spl = spl.filtered(lambda line: not line.product_barcode)
                    if spl:
                        spl[0].product_uom_qty += 1
                        return True
                    else:
                        spl = self.env['stock.move'].create({
                            'name': self.name,
                            'picking_id': self.id,
                            'product_id': product_id,
                            'product_uom_qty': 1,
                            'picking_type_id': self.picking_type_id.id,
                            'location_id': self.location_id.id,
                            'location_dest_id': self.location_dest_id.id,
                            # 'sequence': ((self.order_line and self.order_line[-1].sequence + 1) or 10),
                            # put it at the end of the order
                        })
                        return True
                else:
                    sol = self.env['stock.move'].create({
                        'picking_id': self.id,
                        'name': self.name,
                        'product_id': product_id,
                        'product_uom_qty': 1,
                        'picking_type_id': self.picking_type_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        # 'sequence': ((self.order_line and self.order_line[-1].sequence + 1) or 10),
                    })
                return True

    def _default_order_line_values(self):
        default_data = super()._default_order_line_values()
        new_default_data = self.env['stock.move']._get_product_catalog_lines_data()
        return {**default_data, **new_default_data}

    def _get_action_add_from_catalog_extra_context(self):
        return {
            **super()._get_action_add_from_catalog_extra_context(),
            # 'product_catalog_currency_id': self.currency_id.id,
            # 'product_catalog_digits': self.order_line._fields['price_unit'].get_digits(self.env),
        }

    def _get_product_catalog_domain(self):
        pass
        # return expression.AND([super()._get_product_catalog_domain(), [('sale_ok', '=', True)]])

    def _get_product_catalog_record_lines(self, product_ids):
        grouped_lines = defaultdict(lambda: self.env['stock.move'])
        for line in self.move_ids_without_package:
            if line.product_id.id not in product_ids:
                continue
            grouped_lines[line.product_id] |= line
        return grouped_lines


class StockMove(models.Model):
    _inherit = 'stock.move'

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
                'quantity': self.product_uom_qty,
                'price': 0,
                'readOnly': self.picking_id._is_readonly() or (self.product_id.sale_line_warn == "block"),
            }
            if self.product_id.sale_line_warn != 'no-message' and self.product_id.sale_line_warn_msg:
                res['warning'] = self.product_id.sale_line_warn_msg
            return res
        elif self:
            self.product_id.ensure_one()
            order_line = self[0]
            order = order_line.picking_id
            res = {
                'readOnly': False,
                'price': 0,
                'quantity': sum(
                    self.mapped(
                        lambda line: line.product_uom_qty
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
