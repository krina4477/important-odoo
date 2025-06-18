# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class InheritInvoiceOrderLines(models.Model):
    _inherit = 'account.move.line'

    margin = fields.Float(string="Margin", compute='_get_margin_invoice')
    cost = fields.Float(string="Cost", compute='_get_cost_invoice')
    margin_percentage = fields.Float(string="Margin (%)", compute='_get_margin_percentage')

    @api.depends('product_id')
    def _get_cost_invoice(self):
        for rec in self:
            if rec.product_id:
                rec.cost = rec.product_id.standard_price
            else:
                rec.cost = 0

    @api.depends('price_unit', 'cost', 'quantity')
    def _get_margin_invoice(self):
        for rec in self:
            if rec.product_id:
                rec.margin = rec.price_subtotal - (rec.cost * rec.quantity)
            else:
                rec.margin = 0

    @api.depends('margin', 'price_subtotal')
    def _get_margin_percentage(self):
        for rec in self:
            if rec.price_subtotal > 0:
                rec.margin_percentage = (rec.margin * 100) / rec.price_subtotal
            else:
                rec.margin_percentage = 0

