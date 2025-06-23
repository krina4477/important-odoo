# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Purchase Requisition',
        readonly=True,
        copy=True
    )

    @api.model_create_multi
    def create(self, vals):
        for data in vals:
            picking_type = data.get('picking_type_id')
            if picking_type:
                picking_type_id = self.env['stock.picking.type'].sudo().browse(picking_type)
                # if picking_type_id.code == 'internal' and not self._context.get('from_valid_source'):
                #     raise Warning(_("You can't create internal transfer from this screen\n "
                #                     "You should use incoming and outgoing screen\n"
                #                     "This incident has been reported to the admins"))
        res = super(StockPicking, self.sudo()).create(vals)
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisitions Line',
        copy=True
    )
