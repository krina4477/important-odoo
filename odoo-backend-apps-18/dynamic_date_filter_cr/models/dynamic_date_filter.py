# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from lxml import etree


class DynamicDateFilter(models.Model):
    _name = 'dynamic.date.filter'
    _description = 'Dynamic Date Filter'

    name = fields.Char('Filter Name', required=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True, ondelete='cascade')
    model_name = fields.Char('Model Name', related='model_id.model', store=True)
    ir_model_fields_id = fields.Many2one('ir.model.fields', string='Date Field',required=True,
                                         ondelete='cascade',
                                         domain="[('ttype','=','serialized'), ('model_id', '=', model_id)]",
                                         help="If set, this field will be stored in the sparse structure of the "
                                              "serialization field, instead of having its own database column. "
                                              "This cannot be changed after creation.",
                                         )
    new_view_id = fields.Many2one('ir.ui.view', string='View', required=True, ondelete="cascade")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], 'State', default='draft')
    today = fields.Boolean('Today')
    today_ir_filter_id = fields.Many2one('ir.filters', 'Today Filter')
    month = fields.Boolean('Last Month')
    month_ir_filter_id = fields.Many2one('ir.filters', 'Last Month Filter')
    year = fields.Boolean('Last Year')
    year_ir_filter_id = fields.Many2one('ir.filters', 'Last Year Filter')

    def confirm_filter(self):
        for filter in self:
            node = etree.fromstring(filter.new_view_id.arch_base)
            if filter.ir_model_fields_id.ttype == 'date':
                if filter.today:
                    newKid = etree.Element('filter')
                    newKid.set('name', 'today')
                    newKid.set('string', 'Todays')
                    newKid.set('domain', '[["' + str(
                        filter.ir_model_fields_id.name) + '", "=", context_today().strftime("%Y-%m-%d")]]')
                    node.insert(0, newKid)
                if filter.month:
                    newKid = etree.Element('filter')
                    newKid.set('name', 'month')
                    newKid.set('string', 'Last 30 Days')
                    newKid.set('domain', '[["' + str(
                        filter.ir_model_fields_id.name) + '", ">=", (context_today()-relativedelta(months=1)).strftime("%Y-%m-%d")], ["' + str(
                        filter.ir_model_fields_id.name) + '", "<=", context_today().strftime("%Y-%m-%d")]]')
                    node.insert(0, newKid)
                if filter.year:
                    newKid = etree.Element('filter')
                    newKid.set('name', 'year')
                    newKid.set('string', 'Last 365 Days')
                    newKid.set('domain', '[["' + str(
                        filter.ir_model_fields_id.name) + '", ">=", (context_today()-relativedelta(years=1)).strftime("%Y-%m-%d")], ["' + str(
                        filter.ir_model_fields_id.name) + '", "<=", context_today().strftime("%Y-%m-%d")]]')
                    node.insert(0, newKid)
            elif filter.ir_model_fields_id.ttype == 'datetime':
                if filter.today:
                    newKid = etree.Element('filter')
                    newKid.set('name', 'today')
                    newKid.set('string', 'Todays')
                    newKid.set('domain', '[["' + str(
                        filter.ir_model_fields_id.name) + '", ">=", context_today().strftime("%Y-%m-%d 00:00:00")], ["' + str(
                        filter.ir_model_fields_id.name) + '", "<=", context_today().strftime("%Y-%m-%d 23:59:59")]]')
                    node.insert(0, newKid)
                if filter.month:
                    newKid = etree.Element('filter')
                    newKid.set('name', 'month')
                    newKid.set('string', 'Last 30 Days')
                    newKid.set('domain', '[["' + str(
                        filter.ir_model_fields_id.name) + '", ">=", (context_today()-relativedelta(months=1)).strftime("%Y-%m-%d 00:00:00")], ["' + str(
                        filter.ir_model_fields_id.name) + '", "<=", context_today().strftime("%Y-%m-%d 23:59:59")]]')
                    node.insert(0, newKid)
                if filter.year:
                    newKid = etree.Element('filter')
                    newKid.set('name', 'year')
                    newKid.set('string', 'Last 365 Days')
                    newKid.set('domain', '[["' + str(
                        filter.ir_model_fields_id.name) + '", ">=", (context_today()-relativedelta(years=1)).strftime("%Y-%m-%d 00:00:00")], ["' + str(
                        filter.ir_model_fields_id.name) + '", "<=", context_today().strftime("%Y-%m-%d 23:59:59")]]')
                    node.insert(0, newKid)
            final_view = etree.tostring(node, encoding='unicode')
            filter.new_view_id.arch_base = final_view
            filter.state = 'confirm'

    def remove_filter(self):
        for filter in self:
            if filter.today:
                filter.remove_element_from_view(name='today')
            if filter.month:
                filter.remove_element_from_view(name='month')
            if filter.year:
                filter.remove_element_from_view(name='year')
            filter.state = 'draft'

    def remove_element_from_view(self, name=''):
        if name:
            for filter in self:
                node = etree.fromstring(filter.new_view_id.arch_base)
                for ele in node.iter():
                    if name == 'today':
                        if 'today' in ele.values():
                            node.remove(ele)
                    if name == 'month':
                        if 'month' in ele.values():
                            node.remove(ele)
                    if name == 'year':
                        if 'year' in ele.values():
                            node.remove(ele)
                final_view = etree.tostring(node, encoding='unicode')
                filter.new_view_id.arch_base = final_view

    def unlink(self):
        for filter in self:
            if filter.today:
                filter.remove_element_from_view(name='today')
            if filter.month:
                filter.remove_element_from_view(name='month')
            if filter.year:
                filter.remove_element_from_view(name='year')
        return super(DynamicDateFilter, self).unlink()
