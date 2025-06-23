# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    use_same_dn = fields.Boolean(string='Use Same DN',
        help='Indicate that we have to use same DN in the return or need a new DN.', default=True)

    def _prepare_picking_default_values(self):
        res = super()._prepare_picking_default_values()
        res['is_return_order'] = True
        if self.use_same_dn:
            res['dn_id'] = self.picking_id.dn_id.id
        # else:
        #     res['is_sale_return_new_dn'] = True
        return res
