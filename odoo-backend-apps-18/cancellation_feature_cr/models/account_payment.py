# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_for_all_operations(self, payment_cancel_type):
        account_move_obj = self.env['account.move'].sudo()
        for rec in self:
            invoice = account_move_obj.search([('name', '=', rec.ref)])
            if payment_cancel_type == 'cancel':
                if rec.state == 'posted':
                    rec.state = 'draft'
                    rec.state = 'cancel'
                    invoice.button_draft()
                    invoice.button_cancel()

            elif payment_cancel_type == 'cancel_reset':
                if rec.state == 'posted':
                    rec.action_draft()
                    invoice.button_draft()

            elif payment_cancel_type == 'cancel_delete':
                if rec.state == 'posted':
                    rec.action_draft()
                    rec.action_cancel()
                    invoice.button_draft()
                    invoice.state = 'cancel'
                    rec.unlink()

    # CANCEL BUTTON METHOD
    def action_cancel(self):
        payment_cancel_type = self.env['ir.config_parameter'].sudo().get_param(
            'cancellation_feature_cr.payment_cancel_type')

        self.action_for_all_operations(payment_cancel_type)

        if payment_cancel_type == 'cancel_delete':
            action = self.env["ir.actions.act_window"]._for_xml_id('account.action_account_payments')
            action['tag'] = 'reload'
            return action

    # SERVER ACTIONS METHODS
    def account_payment_cancel_server_action_method(self):
        payment_cancel_type = 'cancel'

        self.action_for_all_operations(payment_cancel_type)

    def account_payment_cancel_draft_server_action_method(self):
        payment_cancel_type = 'cancel_reset'

        self.action_for_all_operations(payment_cancel_type)

    def account_payment_cancel_delete_server_action_method(self):
        payment_cancel_type = 'cancel_delete'

        self.action_for_all_operations(payment_cancel_type)
        if payment_cancel_type == 'cancel_delete':
            action = self.env["ir.actions.act_window"]._for_xml_id('account.action_account_payments')
            return action
