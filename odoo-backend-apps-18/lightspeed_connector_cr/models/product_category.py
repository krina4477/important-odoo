# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import models, api, _, fields


class ProductCategory(models.Model):
    _name = 'product.category'
    _inherit = ['product.category','lightspeed.mixin']


    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductCategory, self).create(vals_list)
        if res.shop_id:
            res.shop_id._create_product_category(categ_id=res.id)
        return res


    def write(self, vals):
        res = super(ProductCategory, self).write(vals)
        for rec in self:
            if rec.shop_id:
                rec.shop_id._update_product_category(categ_id=rec.id)
        return res
