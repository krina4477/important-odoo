# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


from odoo import _,fields, models


class QuestionAnswer(models.Model):
    _name = 'question.answer'
    _description = 'Questions and Answers'

    question = fields.Char(string='Question')
    answer_ids = fields.Many2many('answer.answer',string="Answer")
    product_id = fields.Many2one("product.template", string="Product", required=True)
    user_id = fields.Many2one("res.users", string="Asked By", default=lambda self: self.env.user)
    is_published = fields.Boolean("Published", default=False)

    
    
class Answer(models.Model):
    _name = 'answer.answer'
    _description = 'Answers'
    
    name = fields.Char('Name')
    user_id = fields.Many2one("res.users", string="Given By", default=lambda self: self.env.user)