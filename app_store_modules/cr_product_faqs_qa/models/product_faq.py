# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


from odoo import _, api, fields, models


class ProductFAQs(models.Model):
    _name = 'product.faq'
    _description = 'Product FAQs'

    question = fields.Char(string='Question')
    answer = fields.Text(string="Answer")
    product_id = fields.Many2one("product.template", string="Product", required=True)
    user_id = fields.Many2one("res.users", string="Asked By", default=lambda self: self.env.user)
    is_published = fields.Boolean("Published", default=False)
