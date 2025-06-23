from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pos_config_id = fields.Many2one(
        'pos.config', 
        string="POS Configuration", 
        readonly=True, 
        store=True, 
        related='move_id.pos_config_id'
    )
    pos_session_id = fields.Many2one(
        'pos.session', 
        string="POS Session", 
        readonly=True, 
        store=True, 
        related='move_id.pos_session_id'
    )
