# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_for_all_operations(self, invoice_cancel_type):
        account_payment_object = self.env['account.payment'].sudo()
        for rec in self:
            payments = account_payment_object.search([('ref', '=', rec.name), ('state', '=', 'posted')])
            if invoice_cancel_type == 'cancel':
                for payment in payments:
                    payment.state = 'draft'
                    payment.state = 'cancel'
                rec.button_draft()
                # rec.button_cancel()

            elif invoice_cancel_type == 'cancel_reset':
                for payment in payments:
                    payment.state = 'draft'
                    payment.state = 'cancel'
                rec.button_draft()

            elif invoice_cancel_type == 'cancel_delete':
                for payment in payments:
                    payment.action_draft()
                    payment.action_cancel()
                    payment.unlink()
                rec.state = 'draft'
                rec.state = 'cancel'
                rec.write({'name': ''})
                rec.unlink()

    # CANCEL BUTTON METHOD
    def button_cancel(self):
        invoice_cancel_type = self.env['ir.config_parameter'].sudo().get_param(
            'cancellation_feature_cr.invoice_cancel_type')

        self.action_for_all_operations(invoice_cancel_type)

        if invoice_cancel_type == 'cancel_delete':
            action = self.env["ir.actions.act_window"]._for_xml_id('account.action_move_out_invoice_type')
            action['tag'] = 'reload'
            return action

        if invoice_cancel_type and not invoice_cancel_type == 'cancel_reset' or not invoice_cancel_type:
            res = super(AccountMove, self).button_cancel()
            return res

    # SERVER ACTIONS METHODS
    def account_move_cancel_server_action_method(self):
        invoice_cancel_type = 'cancel'

        self.action_for_all_operations(invoice_cancel_type)

    def account_move_cancel_draft_server_action_method(self):
        invoice_cancel_type = 'cancel_reset'

        self.action_for_all_operations(invoice_cancel_type)

    def account_move_cancel_delete_server_action_method(self):
        invoice_cancel_type = 'cancel_delete'

        self.action_for_all_operations(invoice_cancel_type)
        if invoice_cancel_type == 'cancel_delete':
            action = self.env["ir.actions.act_window"]._for_xml_id('account.action_move_out_invoice_type')
            return action
