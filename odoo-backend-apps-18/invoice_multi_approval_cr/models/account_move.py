# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


from odoo import models, fields, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_approved = fields.Boolean("Is Approved", default=False, copy=False)
    state = fields.Selection(selection_add=[('need_approval', 'Pre Approve'), ('posted',)], ondelete={'need_approval': 'cascade'})

    def view_invoice_url_menu_action(self):
        return {
            'invoice_menu_id': self.env.ref('account.menu_finance').id,
            'customer_invoice_action_id': self.env.ref('account.action_move_out_invoice_type').id,
            'vendor_invoice_action_id': self.env.ref('account.action_move_in_invoice_type').id,
        }

    def action_post(self):
        is_approval_list = self.env['approval.config'].sudo().search([])

        for invoice in self:
            if invoice.is_approved == False:
                if is_approval_list:
                    amount_total = invoice.amount_total
                    partner_id = invoice.partner_id.id
                    invoice_product_list = []
                    invoice_product_categ_list = []
                    for line in invoice.invoice_line_ids:
                        invoice_product_list.append(line.product_id.id)
                        if line.product_id.categ_id.id:
                            invoice_product_categ_list.append(
                                line.product_id.categ_id.id)
                    match_approval = self.env['approval.config'].sudo().search([('partner_ids', 'in', partner_id),
                                                                                ('product_ids', 'in',
                                                                                 invoice_product_list),
                                                                                ('product_categ_ids', 'in',
                                                                                 invoice_product_categ_list),
                                                                                ('price_range', '<', amount_total)])
                    if match_approval:
                        res = super().action_post()
                        authority_name = []
                        send_user_emails = []
                        approvers_ids = []
                        current_user_name = self.env.user.name

                        for approver in match_approval:
                            for user_id in approver.user_ids.ids:
                                if user_id not in approvers_ids:
                                    approvers_ids.append(user_id)
                        
                        for user in self.env['res.users'].browse(approvers_ids):
                            send_user_emails.append(user.partner_id.email)
                            authority_name.append(user.name)

                        send_user_emails = ', '.join(send_user_emails)
                        authority_name = ', '.join(authority_name)

                        invoice.state = 'need_approval'
                        invoice.ensure_one()
                        template = self.env.ref(
                            'invoice_multi_approval_cr.invoice_approval_email_template', raise_if_not_found=False)
                        template.write({
                            'email_from': self.env.user.partner_id.email,
                            'email_to': send_user_emails,
                        })
                        email_values = {
                            'email_cc': False,
                            'auto_delete': True,
                            'recipient_ids': [],
                            'partner_ids': [],
                            'scheduled_date': False,
                        }
                        template.with_context(authority_users=authority_name,
                                            system_user=current_user_name,
                                            invoice_menu=self.view_invoice_url_menu_action().get('invoice_menu_id'),
                                            customer_invoice_action=self.view_invoice_url_menu_action().get('customer_invoice_action_id'),
                                            vendor_invoice_action=self.view_invoice_url_menu_action().get('vendor_invoice_action_id'),
                                              ).sudo(
                        ).send_mail(invoice.id, force_send=True, email_values=email_values)
                        res
                    else:

                        invoice.is_approved = True
                        super().action_post()
                else:
                    invoice.is_approved = True
                    super().action_post()
            else:
                super().action_post()

    def action_approved(self):
        self.is_approved = True

    def action_validate(self):
        if self.is_approved == True:
            self.action_post()
        else:
            raise ValidationError(
                _("Invoice must be approved in order to validate it!"))
