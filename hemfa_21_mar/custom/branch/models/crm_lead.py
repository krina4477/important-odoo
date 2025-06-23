# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    branch_ids = fields.Many2many('res.branch', string="Branches")
