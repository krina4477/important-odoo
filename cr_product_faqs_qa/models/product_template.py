# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class Product(models.Model):
    _inherit = 'product.template'

    
    que_ans_ids = fields.One2many('question.answer', 'product_id', string="Question & Answer")
    faqs_ids = fields.One2many('product.faq', 'product_id', string="FAQs")