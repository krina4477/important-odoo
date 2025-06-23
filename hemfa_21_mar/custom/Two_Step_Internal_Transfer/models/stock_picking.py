from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    transit_location_id = fields.Many2one('stock.location', string='Transit Location', domain=[('usage', '=', 'transit')])
    is_two_step_transfer = fields.Boolean(string='Two-Step Transfer')
    two_step_transfer_picking_id = fields.Many2one('stock.picking', string='Two Step Transit Picking', readonly=True)

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for picking in self:
            if picking.is_two_step_transfer:
                second_picking_vals = picking._prepare_two_step_transfer()
                # Create the second picking
                second_picking = self.env['stock.picking'].create(second_picking_vals)
                # Automatically set the second picking to Ready state
                second_picking.action_assign()
                # Post a message in the chatter with a link to the second picking
                picking.message_post(body=f"Second transfer <a href='#' data-oe-model='stock.picking' data-oe-id='{second_picking.id}'>{second_picking.name}</a> created from transit location to the final destination and set to Ready.")

        return res

    def _prepare_two_step_transfer(self):
        """Create the second stock.picking operation using stock.move.line for detailed operations."""
        second_picking_vals = {}
        for picking in self:
            if picking.is_two_step_transfer and picking.transit_location_id:
                
                # Step 1: Force the current picking lines to use the transit location as the destination
                for move_line in picking.move_line_ids:
                    move_line.location_dest_id = picking.transit_location_id

                # Step 2: Prepare the values for the second picking (from transit to final destination)
                # Ensure warehouse for second picking is based on the destination location's warehouse
                warehouse_dest = self.env['stock.warehouse'].search([('lot_stock_id', '=', picking.location_dest_id.id)], limit=1)
                
                if not warehouse_dest:
                    raise ValueError(f"No warehouse found for location {picking.location_dest_id.display_name}")

                second_picking_vals = {
                    'origin': picking.name,  # Use the name of the first picking
                    'location_id': picking.transit_location_id.id,  # From transit location
                    'location_dest_id': picking.location_dest_id.id,  # Final destination from the original picking
                    'picking_type_id': warehouse_dest.int_type_id.id,  # Assign the picking type based on the destination warehouse
                    'two_step_transfer_picking_id': picking.id,
                    'move_ids_without_package': [(0, 0, {
                        'name': move_line.product_id.name,  # Set a name for the move (product name)
                        'product_id': move_line.product_id.id,
                        'product_uom_qty': move_line.qty_done,  # Quantity moved
                        'product_uom': move_line.product_uom_id.id,
                        'location_id': picking.transit_location_id.id,  # From transit location
                        'location_dest_id': picking.location_dest_id.id,  # Final destination location
                    }) for move_line in picking.move_line_ids],
                    'state': 'confirmed',  # Set the second picking status to 'Ready' (confirmed) instead of 'Draft'
                }
        return second_picking_vals
