from odoo import models, fields, api

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    @api.model
    def create(self, vals):
        res = super(StockValuationLayer, self).create(vals)
        if 'create_date' not in vals:
            res.create_date = fields.Datetime.now()
        return res
