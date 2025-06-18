from odoo import models, fields

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_multi_currency = fields.Boolean(string="Enable Multi-Currency")
    currency_id = fields.Many2one('res.currency', string="Default POS Currency")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_multi_currency = fields.Boolean(string="Enable Multi-Currency")
    currency_id = fields.Many2one('res.currency', 'Currency', related='pos_config_id.currency_id', readonly=False)
