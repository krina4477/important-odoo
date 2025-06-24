# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_shop = fields.Boolean(string="Shop Product", default=False, copy=False)
    is_shipping_and_billing_address = fields.Boolean(string="Is Shipping and Billing Address")

    def update_shipping_billing_address(self, delivery_address_vals, billing_address_vals, same_billing_address=True):
        self = self.sudo()
        if not self.partner_id or self.env.user.id == self.env.ref('base.public_user').id:
            self.write({
                        'partner_id': self.partner_id.create(delivery_address_vals)
                    })
        else:
            self.partner_id.write(delivery_address_vals)
        if same_billing_address:
            self.write({
                'partner_invoice_id': self.partner_id.id,
                'partner_shipping_id': self.partner_id.id,
            })
        else:
            if billing_address_vals:
                if self.partner_shipping_id:
                    self.partner_shipping_id.sudo().write(billing_address_vals)
                else:
                    self.write({
                                'partner_invoice_id': self.partner_id.id,
                                'partner_shipping_id': self.partner_shipping_id.with_context(default_type='delivery').sudo().create(billing_address_vals)
                            })


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_delivery_description(self):
        return self.product_id.description_pickingout