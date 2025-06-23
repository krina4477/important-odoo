from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

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

    def _create_picking_from_pos_order_lines(self, location_dest_id, lines, picking_type, partner=False):
        pickings = super()._create_picking_from_pos_order_lines(location_dest_id, lines, picking_type, partner)
        if lines and lines[0].order_id.session_id:
            pickings.write({
                'pos_config_id': lines[0].order_id.session_id.config_id.id,
                'pos_session_id': lines[0].order_id.session_id.id,
            })
        # Update related valuation layers
        pickings._update_stock_valuation_layers()
        return pickings

    def _update_stock_valuation_layers(self):
        """Ensure valuation layers are updated after picking creation."""
        for picking in self:
            for move in picking.move_ids:  # Corrected from 'move_lines' to 'move_ids'
                self.env['stock.valuation.layer']._update_layers_from_move(move)
