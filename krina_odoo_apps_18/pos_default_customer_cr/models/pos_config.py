# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    customer_id = fields.Many2one('res.partner', 'Customer')


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    customer_id = fields.Many2one('res.partner', 'Customer', related='pos_config_id.customer_id', readonly=False)
