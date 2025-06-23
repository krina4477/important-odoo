# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def compare_record(self):
        active_ids = self.env.context.get('active_ids')
        if len(active_ids) < 2 or len(active_ids) > 2:
            raise ValidationError(
                _('Please, you must select two records to compare the values!'))
        compare_record_lines = []
        ir_model_obj=self.env['ir.model.fields']
        for field_name in self._fields.keys():

            old_values = self.search_read(fields=[field_name], domain=[('id', '=', active_ids[0])])[0].get(field_name)
            new_values = self.search_read(fields=[field_name], domain=[('id', '=', active_ids[0])])[0].get(field_name)

            ir_model_field=ir_model_obj.search([('model','=','sale.order'),('name','=',field_name)])
            if ir_model_field.ttype == 'many2one' and (old_values != False or new_values != False):
                compare_record_lines.append((0, 0, {
                    'check_field': field_name,
                    'old_value': old_values[1],
                    'new_value': old_values[1]
                }))
            else:
                compare_record_lines.append((0, 0, {
                    'check_field': field_name,
                    'old_value': self.search_read(fields=[field_name], domain=[('id', '=', active_ids[0])])[0].get(field_name),
                    'new_value': self.search_read(fields=[field_name], domain=[('id', '=', active_ids[1])])[0].get(field_name)
                }))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compare Record'),
            'res_model': 'wiz.compare.record',
            'view_mode': 'form',
            'context': {'default_compare_record_ids': compare_record_lines},
            'target': 'new',
        }
