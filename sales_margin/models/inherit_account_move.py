# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class InheritAccountMove(models.Model):
    _inherit = 'account.move'

    total_margin = fields.Float(string="Total Margin Amount:", compute='_get_total_margin')
    total_margin_percentage = fields.Float(string="Margin (%):", compute='_get_total_margin_percentage')

    @api.depends('invoice_line_ids')
    def _get_total_margin(self):
        for rec in self:
            if rec.invoice_line_ids:
                rec.total_margin = sum(rec.invoice_line_ids.mapped('margin'))

            else:
                rec.total_margin = 0

    @api.depends('invoice_line_ids', 'total_margin')
    def _get_total_margin_percentage(self):
        for rec in self:
            if rec.invoice_line_ids:
                total_cost = sum(rec.invoice_line_ids.mapped('price_subtotal'))
                if total_cost > 0:
                    rec.total_margin_percentage = (rec.total_margin * 100) / total_cost
                else:
                    rec.total_margin_percentage = 0

            else:
                rec.total_margin_percentage = 0
