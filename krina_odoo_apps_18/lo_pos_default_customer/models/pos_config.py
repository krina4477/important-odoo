# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    partner_id = fields.Many2one('res.partner', 'Customer')


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    partner_id = fields.Many2one('res.partner', 'Customer', related='pos_config_id.partner_id', readonly=False)
