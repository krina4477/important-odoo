from odoo import models, fields, api

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    pos_config_id = fields.Many2one(
        'pos.config', 
        string="POS Configuration", 
        readonly=True, 
        store=True
    )
    pos_session_id = fields.Many2one(
        'pos.session', 
        string="POS Session", 
        readonly=True, 
        store=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure POS fields are set during creation."""
        layers = super(StockValuationLayer, self).create(vals_list)
        for layer in layers:
            if layer.stock_move_id:
                layer.write({
                    'pos_config_id': layer.stock_move_id.pos_config_id.id,
                    'pos_session_id': layer.stock_move_id.pos_session_id.id,
                })
        return layers

    @api.model
    def _update_layers_from_move(self, move):
        """Update POS fields in valuation layers based on the stock move."""
        layers = self.search([('stock_move_id', '=', move.id)])
        for layer in layers:
            layer.write({
                'pos_config_id': move.pos_config_id.id,
                'pos_session_id': move.pos_session_id.id,
            })
