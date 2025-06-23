from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    pos_config_id = fields.Many2one(
        'pos.config', 
        string="POS Configuration", 
        readonly=True, 
        store=True, 
        related='picking_id.pos_config_id'
    )
    pos_session_id = fields.Many2one(
        'pos.session', 
        string="POS Session", 
        readonly=True, 
        store=True, 
        related='picking_id.pos_session_id'
    )

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        if self.group_id and self.group_id.pos_order_id:
            vals.update({
                'pos_config_id': self.group_id.pos_order_id.session_id.config_id.id,
                'pos_session_id': self.group_id.pos_order_id.session_id.id,
            })
        return vals
