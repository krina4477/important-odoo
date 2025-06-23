# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


from odoo import models, fields


class ApprovalConfig(models.Model):
    _name = 'approval.config'

    user_ids = fields.Many2many('res.users', string="Approvers", required=True)
    product_ids = fields.Many2many('product.product', string="Products", required=True)
    product_categ_ids = fields.Many2many('product.category', string="Product categories", required=True)
    partner_ids = fields.Many2many('res.partner', string="Partners", required=True)
    price_range = fields.Float(string='Total Greater than', required=True)


