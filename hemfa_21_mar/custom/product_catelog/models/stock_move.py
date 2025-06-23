from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'
    product_barcode = fields.Char(string='Barcode')

    # === ACTION METHODS ===#

    def action_add_from_catalog(self):
        order = self.env['stock.picking'].browse(self.env.context.get('picking_id'))
        return order.action_add_from_catalog()

    def _get_product_catalog_lines_data(self, **kwargs):
        """ Override of `purchase` to add the delivered quantity.

        :rtype: dict
        :return: A dict with the following structure:
            {
                'deliveredQty': float,
                'quantity': float,
                'price': float,
                'readOnly': bool,
            }
        """
        res = super()._get_product_catalog_lines_data(**kwargs)
        res['deliveredQty'] = 0
        return res