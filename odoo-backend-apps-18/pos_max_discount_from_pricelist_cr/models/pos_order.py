# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    pricelist_label = fields.Char(related='pricelist_id.name')

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['pricelist_id', 'pricelist_label']
        return params
