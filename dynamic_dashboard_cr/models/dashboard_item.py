# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api

class DashboardItem(models.Model):
    _name = 'dashboard.item'
    _description = 'Dashboard Item'

    section_id = fields.Many2one('dashboard.section', string="Section", required=True, ondelete='cascade')
    name = fields.Char("Name", required=True)
    action_id = fields.Many2one('ir.actions.act_window', required=True, string='Action', ondelete="cascade")
    model_name = fields.Char("Model", readonly=True, related="action_id.res_model")
    allow_create = fields.Boolean("Create??")
    filter_id = fields.Many2one('ir.filters', 'Filter', ondelete='cascade')
    view_id = fields.Many2one('ir.ui.view', string="List View")
    icon = fields.Binary("Icon")
    icon_filename = fields.Char("Filename")

    record_count = fields.Integer("Total Records", compute="_compute_record_count", store=False)

    @api.depends('model_name')
    def _compute_record_count(self):
        for rec in self:
            if rec.model_name:
                try:
                    model = self.env[rec.model_name]
                    rec.record_count = model.search_count([])
                except Exception:
                    rec.record_count = 0
            else:
                rec.record_count = 0