# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class Picking(models.Model):
    _inherit = "stock.picking"

    def _action_cancel(self):
        self.write({'state': 'cancel'})

    def _action_draft(self):
        self.write({'state': 'draft'})

    def action_for_all_operations(self, stock_picking_cancel_type):
        for rec in self:
            picking = rec.filtered(lambda a: a.state == 'done')
            for pick in picking:
                for move in pick.move_ids_without_package:
                    # for move_line in move.move_line_nosuggest_ids:
                    move.quantity = 0
                    move.state = 'draft'
                    move.unlink()
                for move in pick.move_ids_without_package:
                    move.state = 'draft'
                    move.is_locked = False

                if stock_picking_cancel_type == 'cancel':
                    rec._action_cancel()

                elif stock_picking_cancel_type == 'cancel_reset':
                    rec._action_draft()

                elif stock_picking_cancel_type == 'cancel_delete':
                    rec.unlink()

    def action_cancel(self):
        stock_picking_cancel_type = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr'
                                                                                     '.stock_picking_cancel_type')

        self.action_for_all_operations(stock_picking_cancel_type)
        if stock_picking_cancel_type == 'cancel_delete':
            action = self.env["ir.actions.act_window"]._for_xml_id('stock.action_picking_tree_ready')
            return action
        res = super(Picking, self).action_cancel()
        return res

    # SERVER ACTIONS METHODS
    def stock_picking_cancel_server_action_method(self):
        stock_picking_cancel_type = 'cancel'

        self.action_for_all_operations(stock_picking_cancel_type)

    def stock_picking_cancel_draft_server_action_method(self):
        stock_picking_cancel_type = 'cancel_reset'

        self.action_for_all_operations(stock_picking_cancel_type)

    def stock_picking_cancel_delete_server_action_method(self):
        stock_picking_cancel_type = 'cancel_delete'

        self.action_for_all_operations(stock_picking_cancel_type)
        action = self.env["ir.actions.act_window"]._for_xml_id('stock.action_picking_tree_ready')
        return action
