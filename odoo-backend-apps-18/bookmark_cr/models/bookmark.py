# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _, tools


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        info = super().session_info()
        bookmark_dict = self.env['bookmark.bookmark'].sudo().search_read([
            ('model_id', '!=', False)
        ], ['id'])

        bookmark_ids = [bk.get('id') for bk in bookmark_dict]
        bookmarks = self.env['bookmark.bookmark'].sudo().browse(bookmark_ids)
        bookmarks_models = bookmarks.mapped('model_id')
        model_wise_bookmark = {}
        for model in bookmarks_models:
            res_ids = bookmarks.filtered(lambda r: r.model_id.id == model.id).mapped('record_id')
            model_wise_bookmark.update({
                model.model: res_ids
            })

        info['model_bookmarks'] = model_wise_bookmark
        return info

class Bookmark(models.Model):
    _name = 'bookmark.bookmark'
    _description = "Bookmark"

    name = fields.Char()
    model_id = fields.Many2one('ir.model', string="Res Model")
    res_id = fields.Integer(string="Res ID")
    model = fields.Char(string="Model Name")

    record_id = fields.Many2oneReference(string='Record ID', 
                                         help="ID of the target record in the database",
                                         model_field='model')

    user_id = fields.Many2one('res.users')

    record_reference = fields.Char(string='Reference', 
                                   compute='_compute_record_reference', 
                                   readonly=True, 
                                   store=False)

    record_name = fields.Char(string='Record Reference',
                              compute="compute_record_name")

    def open_form_view(self):
        """
            This method is for when click on VIEW button open perticular record form view.
        """
        action ={
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name': _("%s"%(self.model_id.name)),
            'res_model': self.model,
            'res_id': self.record_id
        }
        return action

    @api.depends('model', 'record_id')
    def _compute_record_reference(self):
        for res in self:
            res.record_reference = "%s,%s" % (res.model, res.record_id)


    @api.depends('model', 'record_id')
    def compute_record_name(self):
        """
            This method is for record_reference compute field's method.
        """
        for res in self:
            if res.record_reference:
                search_record = self.env[res.model].sudo().search([('id','=',res.record_id)])
                res.record_name = search_record.name
            else:
                res.record_name = False