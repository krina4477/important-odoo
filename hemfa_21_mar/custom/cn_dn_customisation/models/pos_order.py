# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    return_pos_order_id = fields.Many2one("pos.order", string="Return Order")

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        if res.get("is_return_order") and res.get("old_pos_reference"):
            PosOrder = self.env["pos.order"].search([('pos_reference', '=', res['old_pos_reference'])], limit=1)
            res['return_pos_order_id'] = PosOrder.id
        return res
