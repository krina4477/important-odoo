from odoo import models


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def _loader_params_barcode_line_ids(self):
        result = super(PosSessionInherit,self)._loader_params_barcode_line_ids()
        result['search_params']['fields'].append('allow_negative_sale_price')
        result['search_params']['fields'].append('product_type')
        return result