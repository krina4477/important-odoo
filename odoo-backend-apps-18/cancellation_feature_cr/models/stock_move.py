# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_cancel_move(self):
        self.write({'state': 'cancel'})

    def _action_draft_move(self):
        self.write({'state': 'draft'})

    def action_for_all_operations(self, stock_picking_cancel_type):
        for rec in self:
            if stock_picking_cancel_type == 'cancel':
                rec._action_cancel_move()

            elif stock_picking_cancel_type == 'cancel_reset':
                rec._action_draft_move()

            elif stock_picking_cancel_type == 'cancel_delete':
                rec._action_draft_move()
                rec.unlink()

    def set_stock_quant_quantity(self, move_qty, stock_move):
        stock_quant_object = self.env['stock.quant']
        product = stock_move.product_id
        if stock_move.product_id.tracking == 'none':
            out_stock_quant = stock_quant_object.sudo().search(
                [('product_id', '=', product.id), ('location_id', '=', stock_move.location_id.id)])
            if not out_stock_quant:
                out_stock_quant = stock_quant_object.sudo().create({
                    'product_id': product and product.id or False,
                    'location_id': stock_move.location_id and stock_move.location_id.id or False,
                    'quantity': 0,
                    'product_uom_id': stock_move.product_uom and stock_move.product_uom.id or False,
                })
            if out_stock_quant:
                out_stock_quant[0].quantity = out_stock_quant[0].quantity + move_qty
                if out_stock_quant[0].quantity == 0:
                    out_stock_quant[0].unlink()

            out_stock_quant = stock_quant_object.sudo().search(
                [('product_id', '=', product.id), ('location_id', '=', stock_move.location_dest_id.id)])
            if not out_stock_quant:
                out_stock_quant = stock_quant_object.sudo().create({
                    'product_id': product and product.id or False,
                    'location_id': stock_move.location_id and stock_move.location_id.id or False,
                    'quantity': 0,
                    'product_uom_id': stock_move.product_uom and stock_move.product_uom.id or False,
                })
            if out_stock_quant:
                out_stock_quant[0].quantity = out_stock_quant[0].quantity - move_qty
                if out_stock_quant[0].quantity == 0:
                    out_stock_quant[0].unlink()

        else:
            for line in stock_move.move_line_ids:
                out_stock_quant = stock_quant_object.sudo().search(
                    [('product_id', '=', product.id), ('location_id', '=', stock_move.location_id.id),
                     ('lot_id', '=', line.lot_id.id)])

                if not out_stock_quant:
                    out_stock_quant = stock_quant_object.sudo().create({
                        'product_id': product and product.id or False,
                        'location_id': stock_move.location_id and stock_move.location_id.id or False,
                        'quantity': 0,
                        'product_uom_id': stock_move.product_uom and stock_move.product_uom.id or False,
                        'lot_id': line.lot_id and line.lot_id.id or False,
                    })

                if out_stock_quant:
                    out_stock_quant[0].quantity = out_stock_quant[0].quantity + line.qty_done
                    if out_stock_quant[0].quantity == 0:
                        out_stock_quant[0].unlink()

                out_stock_quant = stock_quant_object.sudo().search(
                    [('product_id', '=', product.id), ('location_id', '=', stock_move.location_dest_id.id),
                     ('lot_id', '=', line.lot_id.id)])

                if not out_stock_quant:
                    out_stock_quant = stock_quant_object.sudo().create({
                        'product_id': product and product.id or False,
                        'location_id': stock_move.location_id and stock_move.location_id.id or False,
                        'quantity': 0,
                        'product_uom_id': stock_move.product_uom and stock_move.product_uom.id or False,
                        'lot_id': line.lot_id and line.lot_id.id or False,
                    })

                if out_stock_quant:
                    out_stock_quant[0].quantity = out_stock_quant[0].quantity - line.qty_done
                    if out_stock_quant[0].quantity == 0:
                        out_stock_quant[0].unlink()

    def set_order_line_quantity(self, stock_move, pick_operation_ids, picking_state):
        for pack_operation_id in pick_operation_ids:
            move_qty = stock_move.product_uom_qty
            if stock_move.quantity_done:
                move_qty = stock_move.quantity_done

            if stock_move.quantity_done:
                if stock_move.sale_line_id:
                    if stock_move.sale_line_id.qty_delivered >= move_qty:
                        stock_move.sale_line_id.qty_delivered = stock_move.sale_line_id.qty_delivered - move_qty
                if stock_move.purchase_line_id:
                    if stock_move.purchase_line_id.qty_received >= move_qty:
                        stock_move.purchase_line_id.qty_received = stock_move.purchase_line_id.qty_received - move_qty
                if stock_move.product_id.type == 'product':
                    self.set_stock_quant_quantity(move_qty, stock_move)

    def _fetch_pickings(self):
        for move in self:
            picking_state = move.picking_id.state
            if move.picking_id.state != 'done':
                move._do_unreserve()
            if move.picking_id.state == 'done' or 'confirmed' and move.picking_id.picking_type_id.code in ['incoming',
                                                                                                           'outgoing']:
                pickings = self.env['stock.move'].sudo().search(
                    [('picking_id', '=', move.picking_id.id), ('product_id', '=', move.product_id.id)])

                self.set_order_line_quantity(move, pickings, picking_state)

    def stock_move_cancel_server_action_method(self):
        stock_picking_cancel_type = 'cancel'
        self._fetch_pickings()
        self.action_for_all_operations(stock_picking_cancel_type)

    def stock_move_cancel_draft_server_action_method(self):
        stock_picking_cancel_type = 'cancel_reset'
        self._fetch_pickings()
        self.action_for_all_operations(stock_picking_cancel_type)

    def stock_move_cancel_delete_server_action_method(self):
        stock_picking_cancel_type = 'cancel_delete'
        self._fetch_pickings()
        self.action_for_all_operations(stock_picking_cancel_type)
        action = self.env["ir.actions.act_window"]._for_xml_id('stock.stock_move_action')
        return action
