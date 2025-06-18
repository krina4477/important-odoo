# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


from odoo import http
from odoo.http import request

class ProductQAController(http.Controller):

    @http.route(['/submit/question/<int:product_id>'], type='http', auth="user", website=True)
    def submit_question(self, product_id, question, **kw):
        request.env['question.answer'].sudo().create({
            'question': question,
            'product_id': product_id,
            'user_id': request.env.user.id,
            'is_published':True,
        })  
        return request.redirect(request.httprequest.referrer or '/')
    
    
    @http.route(['/submit/answer/<int:question_id>'], type='http', auth="user", website=True)
    def submit_answer(self, question_id, **kw):
        answer_text = kw.get('answer') 
        if answer_text:
            new_answer = request.env['answer.answer'].sudo().create({
                'name': answer_text,
                'user_id': request.env.user.id,
            })
            question = request.env['question.answer'].sudo().browse(question_id)
            question.sudo().write({
                'answer_ids': [(4, new_answer.id)],
            })

        return request.redirect(request.httprequest.referrer or '/')
