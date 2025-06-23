from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    def action_add_from_catalog(self):
        order = self.env['account.move'].browse(self.env.context.get('move_id'))
        return order.action_add_from_catalog()

    def _get_product_catalog_lines_data(self, **kwargs):
        """ Override of `sale` to add the delivered quantity.

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


