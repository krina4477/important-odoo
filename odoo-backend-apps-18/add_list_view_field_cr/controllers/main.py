# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import conf, http, _
from odoo.http import content_disposition, Controller, request, route

class AddField(Controller):

    @http.route(['/add_field'], type='json', auth="public", website=True)
    def portal_my_project(self, **kw):
        list = []
        if kw.get('kwargs') and kw.get('kwargs').get('model'):
            field_ids = request.env['ir.model.fields'].sudo().search([('model_id.model', '=', kw.get('kwargs').get('model'))])
            list = [(i.name, i.field_description)for i in field_ids]
        return list