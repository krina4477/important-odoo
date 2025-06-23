# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cancel_order(self):
        self.write({'state': 'cancel'})

    def _draft_order(self):
        self.write({'state': 'draft'})

    def action_for_all_operations(self, so_cancel_type, cancel_delivery, cancel_invoice_payment):
        for rec in self:
            # CANCELLING OF DONE DELIVERY ORDER AND BRING QUANTITIES
            if cancel_delivery == 'True':
                picking = rec.picking_ids.filtered(lambda a: a.state == 'done')
                for pick in rec.picking_ids:
                    for move in pick.move_ids_without_package:
                        move.quantity = 0
                        move.state = 'draft'
                        move.unlink()
                    for move in pick.move_ids_without_package:
                        move.state = 'draft'
                        move.is_locked = False
                    pick.do_unreserve()
                    pick.action_cancel()

            if cancel_invoice_payment == 'True':
                account_payment_object = self.env['account.payment'].sudo()
                invoices = self.invoice_ids.filtered(lambda a: a.state == 'posted')
                for invoice in invoices:
                    payments = account_payment_object.search([('ref', '=', invoice.name), ('state', '=', 'posted')])
                    invoice.state = 'cancel'
                    payments.state = 'cancel'

            # CANCELLATION TYPES
            if so_cancel_type == 'cancel':
                rec._cancel_order()

            elif so_cancel_type == 'cancel_reset':
                rec._draft_order()

            elif so_cancel_type == 'cancel_delete':
                rec._cancel_order()

    # BUTTON METHOD
    def _action_cancel(self):
        so_cancel_type = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr.so_cancel_type')
        cancel_delivery = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr.cancel_do')
        cancel_invoice_payment = self.env['ir.config_parameter'].sudo().get_param(
            'cancellation_feature_cr.cancel_invoice_payment')

        self.action_for_all_operations(so_cancel_type, cancel_delivery, cancel_invoice_payment)
        if so_cancel_type == 'cancel_delete':
            action = self.env["ir.actions.act_window"]._for_xml_id('sale.action_quotations_with_onboarding')
            action['tag'] = 'reload'
            self.unlink()
            return action

        if so_cancel_type and not so_cancel_type == 'cancel_reset' or not so_cancel_type:
            res = super(SaleOrder, self)._action_cancel()
            return res

    # SERVER ACTIONS METHODS
    def so_cancel_server_action_method(self):
        so_cancel_type = 'cancel'
        cancel_delivery = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr.cancel_do')
        cancel_invoice_payment = self.env['ir.config_parameter'].sudo().get_param(
            'cancellation_feature_cr.cancel_invoice_payment')

        self.action_for_all_operations(so_cancel_type, cancel_delivery, cancel_invoice_payment)

    def so_cancel_draft_server_action_method(self):
        so_cancel_type = 'cancel_reset'
        cancel_delivery = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr.cancel_do')
        cancel_invoice_payment = self.env['ir.config_parameter'].sudo().get_param(
            'cancellation_feature_cr.cancel_invoice_payment')

        self.action_for_all_operations(so_cancel_type, cancel_delivery, cancel_invoice_payment)

    def so_cancel_delete_server_action_method(self):
        so_cancel_type = 'cancel_delete'
        cancel_delivery = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr.cancel_do')
        cancel_invoice_payment = self.env['ir.config_parameter'].sudo().get_param(
            'cancellation_feature_cr.cancel_invoice_payment')

        self.action_for_all_operations(so_cancel_type, cancel_delivery, cancel_invoice_payment)

        self.unlink()
        action = self.env["ir.actions.act_window"]._for_xml_id('sale.action_quotations_with_onboarding')
        action['tag'] = 'reload'
        return action
