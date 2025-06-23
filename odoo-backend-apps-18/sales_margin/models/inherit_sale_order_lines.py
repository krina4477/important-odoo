# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class InheritSaleOrderLines(models.Model):
    _inherit = 'sale.order.line'

    margin = fields.Float(string="Margin", compute='_get_margin', digits=(6, 2))
    cost = fields.Float(string="Cost", compute='_get_cost')
    margin_percentage = fields.Float(string="Margin (%)", compute='_get_margin_percentage', digits=(6, 2))

    @api.depends('product_template_id')
    def _get_cost(self):
        for rec in self:
            if rec.product_id:
                rec.cost = rec.product_id.standard_price
            else:
                rec.cost = 0

    @api.depends('cost', 'product_uom_qty')
    def _get_margin(self):
        for rec in self:
            if rec.product_id:
                rec.margin = rec.price_subtotal - (rec.cost * rec.product_uom_qty)
            else:
                rec.margin = 0

    @api.depends('margin', 'price_subtotal')
    def _get_margin_percentage(self):
        for rec in self:
            if rec.price_subtotal > 0:
                rec.margin_percentage = (rec.margin * 100) / rec.price_subtotal
            else:
                rec.margin_percentage = 0
