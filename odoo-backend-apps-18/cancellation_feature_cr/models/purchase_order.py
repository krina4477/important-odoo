# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _cancel_order(self):
        self.write({'state': 'cancel'})

    def _draft_order(self):
        self.write({'state': 'draft'})

    def action_for_all_operations(self, po_cancel_type, cancel_receipt_order, cancel_bill_payment):
        for rec in self:
            # CANCELLING RECEIPT AND DEDUCT QUANTITYS
            if cancel_receipt_order == 'True':
                picking = self.picking_ids.filtered(lambda a: a.state == 'done')
                for pick in picking:
                    for move_line in pick.move_ids_without_package:
                        move_line.quantity = 0
                        move_line.state = 'draft'
                        move_line.unlink()
                    for move in pick.move_ids_without_package:
                        move.state = 'draft'
                        move.is_locked = False
                    pick.state = 'cancel'

            if cancel_bill_payment == 'True':
                account_payment_object = self.env['account.payment'].sudo()
                invoices = self.invoice_ids.filtered(lambda a: a.state == 'posted')
                for invoice in invoices:
                    payments = account_payment_object.search([('ref', '=', invoice.name), ('state', '=', 'posted')])
                    invoice.state = 'cancel'
                    payments.state = 'cancel'

            # CANCELLATION TYPES
            if po_cancel_type == 'cancel':
                rec._cancel_order()

            elif po_cancel_type == 'cancel_reset':
                rec._draft_order()

            elif po_cancel_type == 'cancel_delete':
                rec._cancel_order()

    # BUTTON METHOD
    def button_cancel(self):
        po_cancel_type = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr.po_cancel_type')
        cancel_receipt_order = self.env['ir.config_parameter'].sudo().get_param(
            'cancellation_feature_cr.cancel_receipt_order')
        cancel_bill_payment = self.env['ir.config_parameter'].sudo().get_param(
            'cancellation_feature_cr.cancel_bill_payment')

        self.action_for_all_operations(po_cancel_type, cancel_receipt_order, cancel_bill_payment)

        if po_cancel_type == 'cancel_delete':
            self.unlink()
            action = self.env["ir.actions.act_window"]._for_xml_id('purchase.purchase_rfq')
            action['tag'] = 'reload'
            return action

        if po_cancel_type and not po_cancel_type == 'cancel_reset' or not po_cancel_type:
            res = super(PurchaseOrder, self).button_cancel()
            return res

    # SERVER ACTIONS METHODS
    def po_cancel_server_action_method(self):
        po_cancel_type = 'cancel'
        cancel_receipt_order = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr.cancel_receipt_order')
        cancel_bill_payment = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr.cancel_bill_payment')

        self.action_for_all_operations(po_cancel_type,cancel_receipt_order,cancel_bill_payment)

    def po_cancel_draft_server_action_method(self):
        po_cancel_type = 'cancel_reset'
        cancel_receipt_order = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr.cancel_receipt_order')
        cancel_bill_payment = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr.cancel_bill_payment')

        self.action_for_all_operations(po_cancel_type, cancel_receipt_order, cancel_bill_payment)

    def po_cancel_delete_server_action_method(self):
        po_cancel_type = 'cancel_delete'
        cancel_receipt_order = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr.cancel_receipt_order')
        cancel_bill_payment = self.env['ir.config_parameter'].sudo().get_param('cancellation_feature_cr.cancel_bill_payment')

        self.action_for_all_operations(po_cancel_type, cancel_receipt_order, cancel_bill_payment)
        self.unlink()
        action = self.env["ir.actions.act_window"]._for_xml_id('purchase.purchase_rfq')
        action['tag'] = 'reload'
        return action
