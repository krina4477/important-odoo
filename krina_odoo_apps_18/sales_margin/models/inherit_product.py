# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class InheritProducts(models.Model):
    _inherit = 'product.product'

    margin = fields.Float(string="Margin", compute='_get_margin')

    @api.depends('standard_price', 'lst_price')
    def _get_margin(self):
        if self.standard_price or self.lst_price:
            self.margin = self.lst_price - self.standard_price

        else:
            self.margin = 0

