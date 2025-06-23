# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from datetime import timedelta
from itertools import groupby
import time
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from odoo.tools.sql import create_index

from odoo.addons.payment import utils as payment_utils


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'product.catalog.mixin']
    _description = "Sales Order"

    def _update_order_line_globle_click(self, product_id, quantity, **kwargs):
        """ Update sale order line information for a given product or create a
        new one if none exists yet.
        :param int product_id: The product, as a `product.product` id.
        :return: The unit price of the product, based on the pricelist of the
                 sale order and the quantity selected.
        :rtype: float
        """
        sol = self.order_line.filtered(lambda line: line.product_id.id == product_id)

        if sol:
            quantity_sum = sum([i.product_uom_qty for i in sol])
            sol = sol.sorted(key=lambda line: line.id, reverse=True)
            sol = sol[0]
            if quantity != 0:
                sol.product_uom_qty += (quantity - quantity_sum)
            elif self.state in ['draft', 'sent']:
                price_unit = self.pricelist_id._get_product_price(
                    product=sol.product_id,
                    quantity=1.0,
                    currency=self.currency_id,
                    date=self.date_order,
                    **kwargs,
                )
                sol.unlink()
                return price_unit
            else:
                sol.product_uom_qty = 0
        elif quantity > 0:
            print("==========c=c=c=c=c=c=c=c")
            sol = self.env['sale.order.line'].create({
                'order_id': self.id,
                'product_id': product_id,
                'product_barcode': self.env['product.product'].browse(product_id).barcode_line_ids.display_name,
                'product_uom_qty': quantity,
                'sequence': ((self.order_line and self.order_line[-1].sequence + 1) or 10),
                # put it at the end of the order
            })

        return sol.price_unit

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
        sol = self.order_line

        sol_line = sol.filtered(lambda line: line.product_barcode == str(barcode_cutom))

        if len(sol_line.ids) >1:
            quantity_dup = 0
            for i in sol_line[1:]:
                quantity_dup += i.product_uom_qty
                i.unlink()
            sol_line[0].product_uom_qty += quantity_dup

        print("=================================dd'd''", sol)
        print("=================================dd'd''", barcode_cutom)

        if sol_line:
            print("===================c=c=c=c=c=c")
            new_qty = sol_line[0].product_uom_qty + 1
            self.env.cr.execute("""
                UPDATE sale_order_line
                SET product_uom_qty = %s, write_date = now(), write_uid = %s
                WHERE id = %s
            """, (new_qty, self.env.uid, sol_line[0].id))
            self.env.cr.commit()
            return True
        else:
            dynamic_barcode = self.env['product.template.barcode'].search([('name', '=', str(barcode_cutom))], limit=1)
            if dynamic_barcode:
                if sol_line:
                    new_qty = sol_line[0].product_uom_qty + 1
                    self.env.cr.execute("""
                                    UPDATE sale_order_line
                                    SET product_uom_qty = %s, write_date = now(), write_uid = %s
                                    WHERE id = %s
                                """, (new_qty, self.env.uid, sol_line[0].id))
                    self.env.cr.commit()
                    return True
                else:
                    # Compute the next sequence number only once
                    next_sequence = (self.order_line and self.order_line[-1].sequence + 1) or 10

                    for attempt in range(3):
                        try:
                            # Create the sale order line using the ORM
                            self.env['sale.order.line'].create({
                                'order_id': self.id,
                                'customer_lead': 1,
                                'product_id': dynamic_barcode.product_id.id,
                                'name': dynamic_barcode.product_id.name,
                                'price_unit': dynamic_barcode.price,
                                'product_uom_qty': 1,
                                'sequence': next_sequence,
                                'product_uom': dynamic_barcode.unit.id,
                                'product_barcode': barcode_cutom,
                            })
                            break
                        except Exception as e:
                            if 'could not serialize access due to concurrent update' in str(e) and attempt < 2:
                                # Wait briefly before retrying
                                time.sleep(0.5)
                            else:
                                raise e

                    # Note: Do not call self.env.cr.commit() here. Let Odoo manage the transaction.
                    return True

            else:
                if sol:
                    sol = sol.filtered(lambda line: not line.product_barcode)
                    if sol:
                        new_qty = sol[0].product_uom_qty + 1
                        self.env.cr.execute("""
                                                          UPDATE sale_order_line
                                                          SET product_uom_qty = %s, write_date = now(), write_uid = %s
                                                          WHERE id = %s
                                                      """, (new_qty, self.env.uid, sol.id))
                        self.env.cr.commit()
                        return True
                    else:
                        next_sequence = (self.order_line and self.order_line[-1].sequence + 1) or 10
                        for attempt in range(3):
                            try:
                                # Create the sale order line using the ORM
                                self.env['sale.order.line'].create({
                                    'order_id': self.id,
                                    'customer_lead': 1,
                                    'product_id': dynamic_barcode.product_id.id,
                                    'name': dynamic_barcode.product_id.name,
                                    'price_unit': dynamic_barcode.price,
                                    'product_uom_qty': 1,
                                    'sequence': next_sequence,
                                    'product_uom': dynamic_barcode.unit.id,
                                    'product_barcode': barcode_cutom,
                                })
                                break



                            except Exception as e:
                                if 'could not serialize access due to concurrent update' in str(e) and attempt < 2:
                                    # Wait briefly before retrying
                                    time.sleep(0.5)
                                else:
                                    raise e

                        print("=-c=c=c=c=c==c=c=c1111111111111111", self.order_line)
                        self.order_line._compute_price_unit()
                        return True
                else:
                    next_sequence = (self.order_line and self.order_line[-1].sequence + 1) or 10
                    for attempt in range(3):
                        try:
                            # Create the sale order line using the ORM
                            self.env['sale.order.line'].create({
                                'order_id': self.id,
                                'customer_lead': 1,
                                'product_id': dynamic_barcode.product_id.id,
                                'name': dynamic_barcode.product_id.name,
                                'price_unit': dynamic_barcode.price,
                                'product_uom_qty': 1,
                                'sequence': next_sequence,
                                'product_uom': dynamic_barcode.unit.id,
                                'product_barcode': barcode_cutom,
                            })
                            break

                        except Exception as e:
                            if 'could not serialize access due to concurrent update' in str(e) and attempt < 2:
                                # Wait briefly before retrying
                                time.sleep(0.5)
                            else:
                                raise e
                return True

    def _default_order_line_values(self):
        default_data = super()._default_order_line_values()
        new_default_data = self.env['sale.order.line']._get_product_catalog_lines_data()
        return {**default_data, **new_default_data}

    def _get_action_add_from_catalog_extra_context(self):
        return {
            **super()._get_action_add_from_catalog_extra_context(),
            'product_catalog_currency_id': self.currency_id.id,
            'product_catalog_digits': self.order_line._fields['price_unit'].get_digits(self.env),
        }

    def _get_product_catalog_domain(self):
        return expression.AND([super()._get_product_catalog_domain(), [('sale_ok', '=', True)]])

    def _get_product_catalog_record_lines(self, product_ids):
        grouped_lines = defaultdict(lambda: self.env['sale.order.line'])
        for line in self.order_line:
            if line.display_type or line.product_id.id not in product_ids:
                continue
            grouped_lines[line.product_id] |= line
        return grouped_lines


class SaleOrderline(models.Model):
    _inherit = 'sale.order.line'

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
                'price': self.price_unit,
                'readOnly': self.order_id._is_readonly() or (self.product_id.sale_line_warn == "block"),
            }
            if self.product_id.sale_line_warn != 'no-message' and self.product_id.sale_line_warn_msg:
                res['warning'] = self.product_id.sale_line_warn_msg
            return res
        elif self:
            self.product_id.ensure_one()
            order_line = self[0]
            order = order_line.order_id
            res = {
                'readOnly': False,
                'price': order_line.price_unit,
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


class ProductProduct(models.Model):
    _inherit = 'product.product'

    type = fields.Selection(related='product_tmpl_id.type', store=True)