# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import api, fields, models, _
from odoo.osv.expression import AND, OR

import json
from datetime import datetime


class PosConfigCacheData(models.Model):
    _name = "pos.config.cache.data"

    config_id = fields.Many2one("pos.config", string="Pos Config")
    model_name = fields.Char("Model Name")
    session_id = fields.Many2one("pos.session", string="Pos Session", domain=[('active', '=', False)])

    def import_cache_data_config(self, config):
        models = [
            'product.product',
            'res.country',
            'res.partner',
            'product.pricelist',
            'res.country.state',
            'pre.define.note',
            'uom.uom',
            'product.template.barcode',
            'product.template.attribute.line',
            'product.template.attribute.value'
        ]

        # Create a new session
        session_id = self.env['pos.session'].create({
            'config_id': config.id,
            'state': 'closed',
            'active': False,
        })

        # Loop through each model and create cache data for each one
        for model_name in models:
            self.env['pos.config.cache.data'].create({
                'config_id': config.id,
                'model_name': model_name,
                'session_id': session_id.id
            })

    def import_cache_all_data_config(self, config):
        models = [
            'product.product'
        ]

        for model in models:
            count = 0
            existing_records = self.env['pos.config.cache.data'].search([
                ('model_name', '=', model),
                ('config_id', '=', config.id),
            ])

            # List to store values for bulk creation
            bulk_create_vals = []

            for record in existing_records:
                print("callll---------------")
                params = getattr(record.session_id, '_loader_params_%s' % model.replace('.', '_'), None)
                self.env['pos.config.cache.model.data'].search([
                    ('model_name', '=', model),
                    ('config_id', '=', config.id)
                ]).unlink()
                data = self.env['pos.config.cache.model.data'].search_read([
                    ('config_id', '=', record.config_id.id),
                    ('model_name', '=', model)
                ], fields=['res_id'])
                ids = []
                for line in data:
                    ids.append(int(line['res_id']))
                selected_fields = self.env[model].search_read([
                    ('id', 'not in', ids),
                    ('available_in_pos', '=', True),
                ], fields=params()['search_params']['fields'])
                record.session_id._process_pos_ui_product_product(selected_fields)
                for product in selected_fields:
                    count = count + 1
                    vals = {
                        'config_id': record.config_id.id,
                        'session_id': record.session_id.id,
                        'model_name': model,
                        'res_id': product.get('id'),
                        'json_data': product[0] if type(product) is list else product,
                        'product_id': int(product.get('id')),
                    }
                    bulk_create_vals.append(vals)

            # Perform bulk create operations
            if bulk_create_vals:
                self.env['pos.config.cache.model.data'].create(bulk_create_vals)

    def import_cache_data(self):
        # Search for all POS config records
        config_ids = self.env['pos.config'].search([])

        # List of models for which cache data needs to be created
        models = [
            'res.country',
            'res.partner',
            'product.pricelist',
            'res.country.state',
            'pre.define.note',
            'uom.uom',
            'product.template.barcode',
            'product.product'
            'product.template.attribute.line',
            'product.template.attribute.value'
        ]

        # Iterate through each configuration record
        for config in config_ids:
            # Search for an existing closed and inactive POS session for the given config
            existing_session = self.env['pos.session'].search([
                ('config_id', '=', config.id),
                ('state', '=', 'closed'),
                ('active', '=', False),
            ], limit=1)

            # If no session exists, create a new one
            if not existing_session:
                session_id = self.env['pos.session'].create({
                    'config_id': config.id,
                    'state': 'closed',
                    'active': False,
                })
            else:
                session_id = existing_session

            # Loop through each model in the models list
            for model_name in models:
                # Check if there is any existing cache data for the given config and model
                existing_record = self.env['pos.config.cache.data'].search_count([
                    ('config_id', '=', config.id),
                    ('model_name', '=', model_name)
                ])

                # If no cache data exists, create new cache data
                if existing_record == 0:
                    self.env['pos.config.cache.data'].create({
                        'config_id': config.id,
                        'model_name': model_name,
                        'session_id': session_id.id
                    })

    def import_cache_all_data(self, pos_config_id):
        models = [
            'product.product',
        ]

        for model in models:
            count = 0
            existing_records = self.env['pos.config.cache.data'].search([('model_name', '=', model), ('config_id', '=', pos_config_id)])

            # List to store values for bulk creation
            bulk_create_vals = []

            for record in existing_records:
                params = getattr(record.session_id, '_loader_params_%s' % model.replace('.', '_'), None)
                self.env['pos.config.cache.model.data'].search([
                    ('model_name', '=', model),
                    ('config_id', '=', record.config_id.id)
                ]).unlink()
                data = self.env['pos.config.cache.model.data'].search_read([
                    ('config_id', '=', record.config_id.id),
                    ('model_name', '=', model)
                ], fields=['res_id'])
                ids = []
                for line in data:
                    ids.append(int(line['res_id']))
                selected_fields = self.env[model].search_read([
                    ('id', 'not in', ids),
                    ('available_in_pos', '=', True),
                ], fields=params()['search_params']['fields'])
                record.session_id._process_pos_ui_product_product(selected_fields)
                for product in selected_fields:
                    count = count + 1
                    vals = {
                        'config_id': record.config_id.id,
                        'session_id': record.session_id.id,
                        'model_name': model,
                        'res_id': product.get('id'),
                        'json_data': product[0] if type(product) is list else product,
                        'product_id': int(product.get('id')),
                    }
                    bulk_create_vals.append(vals)

            # Perform bulk create operations
            if bulk_create_vals:
                self.env['pos.config.cache.model.data'].create(bulk_create_vals)

    def import_update_cache_data(self):
        return True

    
    def pull_cache_all_data(self, pos_config_id):
        models = [
            'res.country',
            'res.partner',
            'product.pricelist',
            'res.country.state',
            'pre.define.note',
            'uom.uom',
            'product.product',
            'product.template.barcode',
            'product.template.attribute.line',
            'product.template.attribute.value'
        ]
        
        bulk_create_vals = []
        model_dict = []
        session_list = []

        # Loop over each model to process them separately
        for model in models:
            count = 0
            existing_records = self.env['pos.config.cache.data'].search([('model_name', '=', model), ('config_id', '=', pos_config_id)])

            for record in existing_records:
                if record.config_id and record.config_id.current_session_id.state == 'opened':
                    session_list.append(record.config_id.current_session_id)
                    
                    self.env['bus.bus']._sendmany(
                    [[record.config_id.current_session_id.user_id.partner_id, 'cache_db_remove', record.config_id.current_session_id.id]])     
                params = getattr(record.config_id.current_session_id, f'_loader_params_{model.replace(".", "_")}', None)
                if not params:
                    continue  # If params is None, skip processing this model
                
                model_dict.append({
                    'model_name': model,
                    'config_id': record.config_id.id
                })
                
                fields = params()['search_params']['fields']
                if model == 'product.template.attribute.line':
                    fields = [f for f in fields if f != 'name']
                    print(f"Fields for {model}: {fields}")
                if model == 'product.product':
                    selected_fields = self.env[model].search_read([
                         ('available_in_pos', '=', True)
                    
                    ], fields=fields)
                elif model == 'product.pricelist':
                    # First, fetch pricelists and initialize a lookup by their IDs
                    pricelists = self.env[model].search_read([], fields=fields)

                    # Create a dictionary mapping pricelist IDs to their respective pricelist objects
                    pricelist_by_id = {pricelist['id']: pricelist for pricelist in pricelists}

                    # Prepopulate the 'items' field in the pricelist dictionary to avoid mutating the list inside loops
                    for pricelist in pricelists:
                        pricelist['items'] = []

                    # Fetch the necessary data for pricelist items
                    pricelist_item_domain = [('pricelist_id', 'in', [p['id'] for p in pricelists])]
                    loaded_data = self._context.get('loaded_data')

                    # Adjust domain for limited product loading if needed
                    if loaded_data and self.config_id.limited_products_loading:
                        product_ids = [p['id'] for p in loaded_data['product.product']]
                        template_ids = [p['product_tmpl_id'][0] for p in loaded_data['product.product']]
                        pricelist_item_domain = self._product_pricelist_item_domain_by_product(template_ids, product_ids, pricelists)

                    # Fetch all pricelist items in a single query
                    pricelist_items = self.env['product.pricelist.item'].search_read(pricelist_item_domain, record.session_id._product_pricelist_item_fields())

                    # Build the items list for each pricelist
                    for item in pricelist_items:
                        pricelist_by_id[item['pricelist_id'][0]]['items'].append(item)

                    # Return the selected fields with updated pricelist items
                    selected_fields = pricelists
                                
                else:     
                    selected_fields = self.env[model].search_read([
                        
                    ], fields=fields)
                config_id = record.config_id.id   
                session_id = record.config_id.current_session_id.id    
                # Prepare the bulk creation values for both 'product.product' and other models
                for item in selected_fields:
                    count += 1
                    # Prepare values for product.product or other models
                    vals = {
                        'config_id': config_id,
                        'session_id': session_id,
                        'model_name': model,
                        'res_id': item['id'],
                        'json_data': item[0] if isinstance(item, list) else item,
                    }
                    
                    # If it's a product.product model, include the 'product_id' field
                    if model == 'product.product':
                        vals['product_id'] = int(item['id'])
                    
                    # Append to the bulk_create_vals
                    bulk_create_vals.append(vals)
                # Trigger the session-specific loader function if available
                # if model == 'res.country':
                #     record.session_id._loader_params_res_country()
                # elif model == 'product.template.barcode':
                #     record.session_id._loader_params_product_template_barcode()
                # elif model == 'res.partner':
                #     record.session_id._loader_params_res_partner()
                # elif model == 'product.pricelist':
                #     record.session_id._product_pricelist_item_fields()
                # elif model == 'uom.uom':
                #     record.session_id._loader_params_uom_uom()
                # elif model == 'pre.define.note' and selected_fields:
                #     record.session_id._get_pos_ui_pre_define_note(selected_fields)
                # elif model == 'res.country.state':
                #     record.session_id._loader_params_res_country_state()
                # elif model == 'product.product':
                #     record.session_id._process_pos_ui_product_product(selected_fields)   
                # elif model == 'product.template.attribute.line':
                #     record.session_id._loader_params_product_template_attribute_line()
                # elif model == 'product.template.attribute.value':
                #     record.session_id._loader_params_product_template_attribute_value()

            print(f"Processed {count} records for model {model}")

        if bulk_create_vals:
            for model in model_dict:
                self.env.cr.execute("""
                    DELETE FROM pos_config_cache_model_data
                    WHERE model_name = %s 
                    AND config_id = %s;
                """, (model['model_name'], model['config_id']))
            # Bulk create the cache data after processing
            if bulk_create_vals:
                self.env['pos.config.cache.model.data'].sudo().create(bulk_create_vals)
        session_list = list(set(session_list))
        for session in session_list:
            self.env['bus.bus']._sendmany(
                    [[session.user_id.partner_id, 'on_pull', session.id]])   
            
    
    
    def _cache_data(self):
        model = self._context.get('model')
        # Fetch all records in one go, avoiding repeated database queries
        existing_records = self.env['pos.config.cache.data'].search([('model_name', '=', model)])

        # Prepare a list to store values for batch create/write
        vals_list = []
        for record in existing_records:
            data = record.config_id.current_session_id.with_context(record=record, custom_method=True).get_details(model, res_id=self._context.get('res_id'))

            # Process data only if available
            if data:
                if model == 'product.product':
                    vals = {
                        'config_id': record.config_id.id,
                        'session_id': record.config_id.current_session_id.id,
                        'model_name': model,
                        'res_id': self._context.get('res_id'),
                        'json_data': data[0] if isinstance(data, list) else data,
                        'product_id': self._context.get('res_id'),

                    }
                    vals_list.append(vals)
                elif model == 'product.pricelist':
                    pricelist_by_id = {pricelist['id']: pricelist for pricelist in data}

                    # Prepopulate the 'items' field in the pricelist dictionary to avoid mutating the list inside loops
                    for pricelist in data:
                        pricelist['items'] = []

                    # Fetch the necessary data for pricelist items
                    pricelist_item_domain = [('pricelist_id', 'in', [p['id'] for p in data])]
                    loaded_data = self._context.get('loaded_data')

                    # Adjust domain for limited product loading if needed
                    if loaded_data and self.config_id.limited_products_loading:
                        product_ids = [p['id'] for p in loaded_data['product.product']]
                        template_ids = [p['product_tmpl_id'][0] for p in loaded_data['product.product']]
                        pricelist_item_domain = self._product_pricelist_item_domain_by_product(template_ids, product_ids, data)

                    # Fetch all pricelist items in a single query
                    pricelist_items = self.env['product.pricelist.item'].search_read(pricelist_item_domain, record.session_id._product_pricelist_item_fields())

                    # Build the items list for each pricelist
                    for item in pricelist_items:
                        pricelist_by_id[item['pricelist_id'][0]]['items'].append(item)

                    # Return the selected fields with updated pricelist items
                    selected_fields = data 
                    vals = {
                        'config_id': record.config_id.id,
                        'session_id': record.config_id.current_session_id.id,
                        'model_name': model,
                        'res_id': self._context.get('res_id'),
                        'json_data': selected_fields[0] if isinstance(selected_fields, list) else selected_fields,

                    }
                    vals_list.append(vals)   
                else:
                    vals = {
                        'config_id': record.config_id.id,
                        'session_id': record.config_id.current_session_id.id,
                        'model_name': model,
                        'res_id': self._context.get('res_id'),
                        'json_data': data[0] if isinstance(data, list) else data,

                    }
                    vals_list.append(vals)
                        

        # Perform batch processing for existing records
        if vals_list:
            # Optimize fetching of existing records by using a dictionary for quick lookup
            existing_record_ids = self.env['pos.config.cache.model.data'].search_read(
                [('config_id', 'in', [val['config_id'] for val in vals_list]),
                 ('model_name', '=', model),
                 ('res_id', '=', self._context.get('res_id'))],
                ['id', 'config_id', 'session_id']
            )

            # existing_record_dict = {(rec['config_id'][0], rec['session_id'][0]): rec['id'] for rec in existing_record_ids}
            existing_record_dict = {(rec['config_id'][0] if rec['config_id'] else None,rec['session_id'][0] if rec['session_id'] else None): rec['id'] for rec in existing_record_ids
            }

            for vals in vals_list:
                record_key = (vals['config_id'], vals['session_id'])
                if record_key in existing_record_dict:
                    # Update existing record
                    self.env['pos.config.cache.model.data'].browse(existing_record_dict[record_key]).write(vals)
                else:
                    # Create a new record
                    self.env['pos.config.cache.model.data'].create(vals)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals_list):
        result = super(ProductProduct, self).create(vals_list)
        if not self._context.get('skip_log'):
            for rec in result:
                self.env['pos.config.cache.data'].with_context(model='product.product', res_id=rec.id)._cache_data()
        return result

    def write(self, vals):
        result = super(ProductProduct, self).write(vals)
        for rec in self:
            if not self._context.get('skip_log'):
                if rec and rec.active:
                    self.env['pos.config.cache.data'].with_context(model='product.product',
                                                                   res_id=rec.id)._cache_data()
        return result
    
    

class ProductPriceList(models.Model):
    _inherit = 'product.pricelist'

    @api.model_create_multi
    def create(self, vals_list):
        result = super(ProductPriceList, self).create(vals_list)
        if not self._context.get('skip_log'):
            for rec in result:
                self.env['pos.config.cache.data'].with_context(model='product.pricelist', res_id=rec.id)._cache_data()
        return result

    def write(self, vals):
        result = super(ProductPriceList, self).write(vals)
        for rec in self:
            if not self._context.get('skip_log'):
                if rec and rec.active:
                    self.env['pos.config.cache.data'].with_context(model='product.pricelist',
                                                                   res_id=rec.id)._cache_data()
        return result    

    def unlink(self):
        for rec in self:
            existing_record_ids = self.env['pos.config.cache.model.data'].search(
                [
                 
                 ('model_name', '=', 'product.pricelist'),
                 ('res_id', '=', rec.id)]
            )
            if existing_record_ids:
                existing_record_ids.unlink()
  
            return super(ProductPriceList, self).unlink()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        result = super(ResPartner, self).create(vals_list)
        if not self._context.get('skip_log'):
            for rec in result:
                self.env['pos.config.cache.data'].with_context(model='res.partner', res_id=rec.id)._cache_data()
        return result

    def write(self, vals):
        result = super(ProductPriceList, self).write(vals)
        for rec in self:
            if not self._context.get('skip_log'):
                if rec and rec.active:
                    self.env['pos.config.cache.data'].with_context(model='res.partner',
                                                                   res_id=rec.id)._cache_data()
        return result 
    
    
    def unlink(self, vals):
        for rec in self:
            existing_record_ids = self.env['pos.config.cache.model.data'].search(
                [
                 
                 ('model_name', '=', 'res.partner'),
                 ('res_id', '=', rec.id)]
            )
            if existing_record_ids:
                existing_record_ids.unlink()
  
            return super(ResPartner, self).unlink(vals)
   



# class ResPartner(models.Model):
#     _inherit = 'res.partner'

#     @api.model_create_multi
#     def create(self, vals_list):
#         result = super(ResPartner, self).create(vals_list)
#         if not self._context.get('skip_log'):
#             for rec in result:
#                 self.env['pos.config.cache.data'].with_context(model='res.partner', res_id=rec.id)._cache_data()
#         return result

#     def write(self, vals):
#         result = super(ProductPriceList, self).write(vals)
#         for rec in self:
#             if not self._context.get('skip_log'):
#                 if rec and rec.active:
#                     self.env['pos.config.cache.data'].with_context(model='res.partner',
#                                                                    res_id=rec.id)._cache_data()
#         return result    



class PosSession(models.Model):
    _inherit = 'pos.session'

    active = fields.Boolean(default=True)

    def get_details(self, model, res_id=None):
        params = getattr(self, '_loader_params_%s' % model.replace('.', '_'), None)
        data = []
        dynamic_model = self.env[model]
        if res_id:
            data = dynamic_model.search_read([('id', '=', res_id)],
                                             fields=params()['search_params']['fields'])

        return data

    # <------------------------- product.product ------------------------->

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        if self._context.get('custom_method', False) and self._context.get('res_id', False):
            result.get('search_params').get('domain').append(('id', '=', self._context.get('res_id')))
            return result
        else:
            return result
