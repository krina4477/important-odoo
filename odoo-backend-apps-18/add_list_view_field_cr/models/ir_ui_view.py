# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class IrUiViewInherit(models.Model):
    _inherit = 'ir.ui.view'

    def inherit_check(self, field, model):
        self.add_field(field, model)

    def add_field(self, field, model):
        if self.inherit_id:
            self.inherit_id.inherit_check(field, model)
        else:
            models_id = self.env['ir.model'].sudo().search([('model', '=', model)])
            field_ids = self.env['ir.model.fields'].sudo().search(
                [('name', 'in', field), ('model_id', '=', models_id.id)])
            html = '<xpath expr="//list" position="inside">'
            for field_id in field_ids:
                if field_id.ttype == 'binary':
                    html += '<field name="' + field_id.name + '" optional="show" widget="image"/>'
                elif field_id.ttype == 'many2many':
                    html += '<field name="' + field_id.name + '" optional="show" widget="many2many_tags"/>'
                else:
                    html += '<field name="' + field_id.name + '" optional="show"/>'
            html += '</xpath>'
            val = {
                'name': 'Add Tree view',
                'type': 'list',
                'model': model,
                'priority': 16,
                'inherit_id': self.id,
                'arch_base': html,
            }
            ir_ui_view_id = self.env['ir.ui.view'].sudo().create(val)
            return ir_ui_view_id
