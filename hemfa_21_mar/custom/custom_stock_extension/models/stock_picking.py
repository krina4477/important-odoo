from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        # Check if the state is 'done' and 'date_done' is not set by the user
        if 'state' in vals and vals['state'] == 'done' and 'date_done' not in vals:
            vals['date_done'] = fields.Datetime.now()  # Set 'date_done' to the current time if not provided
        res = super(StockPicking, self).create(vals)
        return res

    def write(self, vals):
        # Call the super method
        res = super(StockPicking, self).write(vals)
        
        # Ensure 'date_done' is correctly set if state transitions to 'done'
        for record in self:
            # Check if the state is being changed to 'done' and 'date_done' is not provided by the user
            if 'state' in vals and vals['state'] == 'done' and not vals.get('date_done') and not record.date_done:
                record.date_done = fields.Datetime.now()  # Set it to now if not already set and no date provided
        return res
