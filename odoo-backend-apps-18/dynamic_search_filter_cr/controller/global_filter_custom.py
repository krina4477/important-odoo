# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
import logging

from lxml import etree
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class DynamicFilterModel(http.Controller):

    def check_tree_view(self, doc, model_id, view_id, field_name, operator, field_description):
        arch = ''
        field_name = field_name
        if operator == '<':
            operator = '&lt;'
        if operator == '>':
            operator = '&gt;'
        if operator == '>=':
            operator = '&gt;='
        if operator == '<=':
            operator = '&lt;='
        if operator == 'not in':
            operator = 'not ilike'
        if operator == 'in':
            operator = 'ilike'
        field = """<field name="{0}" string="{1}" filter_domain="[('{2}','{3}',self)]"/> """.format(field_name,
                                                                                                    field_description,
                                                                                                    field_name,
                                                                                                    operator)
        arch += """<xpath expr="//search" position="inside">""" + field + """</xpath>"""
        return arch

    @http.route('/dynamicfiltermodel/view', type='json', auth="user")
    def get_filter_value(self, data):
        try:
            action_id = data.get('action_id')
            # view_id = request.env['ir.actions.act_window'].sudo().search([('id', '=', action_id)]).view_id.id
            view_id = request.env['ir.actions.act_window'].sudo().search([('path', '=', action_id)]).search_view_id.id
            # xml_id = view_id
            model = data.get('res_model')
            operator = data.get('operator')
            field_string = data.get('field_string')
            # data_exist_view_id = xml_id
            action_rec = request.env['ir.actions.act_window'].search([('path', '=', action_id)])
            treeview_id = request.env['ir.ui.view'].sudo().search([('id', '=', int(action_rec.search_view_id.id))],
                                                                  limit=1)
            exist_view_id = request.env['ir.ui.view'].sudo().search([('id', '=', int(view_id))], limit=1)
            # exist_view_id = request.env['ir.ui.view'].sudo().search([('id', '=', int(data_exist_view_id))], limit=1)
            model_id = request.env['ir.model'].sudo().search([('model', '=', model)], limit=1).id
            field_id = request.env['ir.model.fields'].sudo().search(
                [('name', '=', field_string), ('model_id', '=', model_id)], limit=1)
            field_name = field_id.name
            field_description = field_id.field_description
            # view_name = request.env['ir.actions.act_window'].sudo().search([('id', '=', action_id)]).view_id.name
            if treeview_id:
                doc = etree.fromstring(treeview_id.arch)
                arch = ''
                is_view_available = request.env['ir.ui.view'].sudo().search(
                    [('name', '=', 'add filter fields for ' + exist_view_id.name)], limit=1)
                arch += self.check_tree_view(doc, model_id, treeview_id, field_name, operator, field_description, )
                view_data = {'name': 'add filter fields for ' + exist_view_id.name,
                             'type': 'search',
                             'model': model,
                             'priority': 1,
                             'inherit_id': treeview_id.id,
                             'mode': 'extension',
                             'arch': arch}
                if is_view_available:
                    node = etree.fromstring(is_view_available.arch_base)
                    # domain_str = """[('{0}','{1}',self)]""".format(field_name, operator)
                    # print("++++++++++domain_str+++++++++++",domain_str)
                    newKid = etree.Element('field')
                    newKid.set('name', field_name)
                    newKid.set('string', field_description)
                    # newKid.set('filter_domain', domain_str)
                    node.insert(0, newKid)
                    final_view = etree.tostring(node, encoding='unicode')
                    is_view_available.write({'arch_base': final_view})
                else:
                    request.env["ir.ui.view"].sudo().create(view_data)
            return {'status': 'success'}
        except Exception as e:
            _logger.error("An error occurred: %s", str(e))
            return {'status': 'error', 'message': str(e)}
