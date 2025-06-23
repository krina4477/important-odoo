# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    branch_id = fields.Many2one('res.branch')






