# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import conf, http, _
from odoo.http import content_disposition, Controller, request, route
import json

class FindsRecords(Controller):

        @http.route(['/finds_records'], type='json')
        def finds_records(self, **kw):
            kw = kw.get('kwargs')
            options_data = kw.get('options')
            new_options_data = options_data.replace('\'', '\"')
            fields_name = json.loads(new_options_data)
            fields = fields_name['fields']
            model = kw.get('model_name')
            field_name = kw.get('fields_name')
            value = kw.get('val')

            records = request.env[model].sudo().search([(field_name, 'ilike', value)])
            record_list = []
            table_header = []
            table_body = []
            vals = {}
            rec_count = 0
            if records:
                for rec in records:
                    same_recod = []
                    for field in fields:
                        rec_count += 1
                        key = 'field_' + str(rec_count)
                        if field not in table_header:
                            table_header.append(field)
                        if type(rec[field]).__name__ == model:
                            if rec[field]:
                                same_recod = rec[field].mapped('name')
                            else:
                                same_recod.append(False)
                        else:
                            same_recod.append(rec[field])
                    table_body.append(same_recod)
                view_id = request.env['ir.ui.view'].search([('model', '=', model),
                                                         ('type', '=', 'tree'),
                                                         ('active', '=', True)
                                                         ], order='id asc', limit=1)

                vals.update({field_name: rec[field_name], key: [field, rec[field]], 'length_rec': len(records),
                             'table_header': table_header, 'table_body': table_body,
                             'view': view_id and view_id.id or '',
                             'model': model, 'dyn_field': field_name, 'dyn_value': value})
                record_list.append(vals)
            return record_list
