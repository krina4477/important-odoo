# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import http,api
from odoo.http import request

class AddRemoveBookmark(http.Controller):

    @http.route('/list_create', type='json', auth='user', csrf=False)
    def listview_create(self,**vals):
        """
            This route is for create bookmark when select single or multiple records and click 
            on Add To Bookmark action then selected records create inside bookmark.bookmark model.        
        """
        kwargs = vals.get('kwargs', {})
        user_id = kwargs.get('user_id') or request.env.user.id
        kwargs['user_id'] = user_id
        vals = vals.get('kwargs')
        model_id = request.env['ir.model'].search([('model', '=', vals.get('model'))])
        if vals.get('new_ids'):
            id_list=[]
            id_list = vals.get('new_ids')
            vals.pop('new_ids')
            for rec_id in id_list:
                book = request.env['bookmark.bookmark'].search([
                    ('res_id', '=', rec_id),
                    ('model_id', '=', model_id.id)
                ])
                if not book:
                    vals['res_id'] = rec_id
                    vals['record_id'] = rec_id
                    vals['model_id'] = model_id.id
                    bookmark = request.env['bookmark.bookmark'].create(vals)
        return True

    @http.route('/form_create', type='json', auth='user', csrf=False)
    def formview_create(self, **vals):
        """
            This route is for create bookmark when inside form view select Add To Bookmark action
            then create bookmark for perticular record.        
        """
        kwargs = vals.get('kwargs', {})
        user_id = kwargs.get('user_id') or request.env.user.id
        kwargs['user_id'] = user_id
        vals = vals.get('kwargs')
        model_id = request.env['ir.model'].search([('model', '=', vals.get('model'))])
        book = request.env['bookmark.bookmark'].search([
                ('res_id', '=', vals.get('res_id')),
                ('model_id', '=', model_id.id)
            ])
        if not book:
            if model_id:
                vals['model_id'] = model_id.id
            bookmark = request.env['bookmark.bookmark'].sudo().create(vals)
        return True
            

    @http.route('/listview_remove', type='json', auth='user', csrf=False)
    def listview_remove(self, **vals):
        """
            This route is for remove bookmark when select single or multiple records and click 
            on Remove Bookmark action then selected records remove inside bookmark.bookmark model.        
        """
        vals=vals.get('kwargs')
        model_id = request.env['ir.model'].search([('model', '=', vals.get('model'))])
        if 'model_id' in vals:
            bookmark_id = request.env['bookmark.bookmark'].sudo().search([
                ('record_id', '=', vals.get('record_id')),
                ('model_id', '=', model_id.id)
            ])
            bookmark_id.unlink()
        if 'record_ids' in vals:
            bookmark_id = request.env['bookmark.bookmark'].sudo().search([
                ('record_id', 'in', vals.get('record_ids')),
                ('model_id', '=', model_id.id)
            ])
            bookmark_id.unlink()
        return True
        
    @http.route('/formview_remove', type='json', auth='user', csrf=False)
    def formview_remove(self, **vals):
        """
            This route is for remove bookmark if record is bookmarked then show Remove Bookmark and 
            when click on Remove Bookmark action then perticular record remove inside bookmark.bookmark 
            model.        
        """
        res = request.env['bookmark.bookmark'].search([('record_id', '=', vals['id'])])
        if vals['id'] == res.record_id:
            res.unlink()
        return True
