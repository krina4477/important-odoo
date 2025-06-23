# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models, _
from lxml import etree


class CreateCustomTab(models.Model):
    _name = 'create.custom.tab'

    is_custom_tab = fields.Boolean('Custom Tab')
    name = fields.Char('Name')
    xml_id = fields.Many2one('ir.ui.view', 'Parent Xml ID')
    current_xml_id = fields.Many2one('ir.ui.view', 'New Xml ID')
    model_id = fields.Many2one('ir.model', string='Model')
    left_field_ids = fields.Many2many('ir.model.fields', 'left_field_ids1', 'left_field_ids2',
                                      string='Left Side Fields')
    right_field_ids = fields.Many2many('ir.model.fields', 'right_field_ids1', 'right_field_ids2',
                                       string='Right Side Fields')

    def unlink(self):
        current_xml_id = self.current_xml_id
        res = super(CreateCustomTab, self).unlink()
        if res:
            current_xml_id.sudo().unlink()
        return res

    def write(self, vals):
        rec = super(CreateCustomTab, self).write(vals)
        if 'name' in vals or 'left_field_ids' in vals or 'right_field_ids' in vals:
            studio_view = self.current_xml_id.sudo()
            parser = etree.XMLParser(remove_blank_text=True)
            arch = etree.fromstring('<data/>', parser=parser)
            xpath_node = etree.SubElement(arch, 'xpath', {
                'expr': "//notebook",
                'position': 'inside'
            })
            xml_node_page = etree.Element('page', {'string': self.name, 'name': 'page_%s' % self.id})
            xml_node_page_left, xml_node_page_right = self.add_columns(xml_node_page)
            for i in self.left_field_ids:
                etree.SubElement(xml_node_page_left, 'field', {'name': i.name, 'string': i.field_description})
            for i in self.right_field_ids:
                etree.SubElement(xml_node_page_right, 'field', {'name': i.name, 'string': i.field_description})
            xpath_node.insert(0, xml_node_page)
            studio_view.arch_db = etree.tostring(arch, encoding='utf-8', pretty_print=True)
        return rec

    @api.model_create_multi
    def create(self, vals_list):
        res = super(CreateCustomTab, self).create(vals_list)
        if res:
            studio_view = self.env['ir.ui.view'].sudo().create({
                'type': res.xml_id.type,
                'model': res.xml_id.model,
                'inherit_id': res.xml_id.id,
                'mode': 'extension',
                'priority': 99,
                'arch': '<data/>',
                'name': "%s Custom Tab %s-%s" % ('Form', str(res.xml_id.id), str(res.id)),
            })
            res.current_xml_id = studio_view.id
            parser = etree.XMLParser(remove_blank_text=True)
            arch = etree.fromstring(studio_view.arch_db, parser=parser)

            xpath_node = etree.SubElement(arch, 'xpath', {
                'expr': "//notebook",
                'position': 'inside'
            })
            xml_node_page = etree.Element('page', {'string': res.name, 'name': 'page_%s' % res.id})
            xml_node_page_left, xml_node_page_right = self.add_columns(xml_node_page)
            for i in res.left_field_ids:
                etree.SubElement(xml_node_page_left, 'field', {'name': i.name, 'string': i.field_description})
            for i in res.right_field_ids:
                etree.SubElement(xml_node_page_right, 'field', {'name': i.name, 'string': i.field_description})
            xpath_node.insert(0, xml_node_page)
            studio_view.arch_db = etree.tostring(arch, encoding='utf-8', pretty_print=True)
        return res

    def add_columns(self, xml_node):
        if xml_node.tag != 'group':
            xml_node_group = etree.SubElement(xml_node, 'group', {})
        else:
            xml_node_group = xml_node
        xml_node_page_left = etree.SubElement(xml_node_group, 'group', {'name': 'left'})
        xml_node_page_right = etree.SubElement(xml_node_group, 'group', {'name': 'right'})
        return xml_node_page_left, xml_node_page_right
