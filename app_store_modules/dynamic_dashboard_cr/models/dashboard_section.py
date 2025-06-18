# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields

class DashboardSection(models.Model):
    _name = 'dashboard.section'
    _description = 'Dashboard Section'

    name = fields.Char("Section Name", required=True)
    company_ids = fields.Many2many('res.company', string="Company")
    item_ids = fields.One2many('dashboard.item', 'section_id', string="Dashboard Items")
