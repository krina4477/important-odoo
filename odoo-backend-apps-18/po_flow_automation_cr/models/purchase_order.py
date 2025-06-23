# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from datetime import date

from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        if self.env.user.po_auto_complete:
            for order in self:
                if order.picking_ids:
                    for picking_id in self.picking_ids:
                        picking_id.action_assign()
                        # picking_id.action_set_quantities_to_reservation()
                        picking_id.button_validate()

                if not order.invoice_ids:
                    order.action_create_invoice()
                if order.invoice_ids:
                    for invoice in order.invoice_ids:
                        if not invoice.invoice_date:
                            invoice.write({'invoice_date': date.today()})
                        invoice.action_post()
                        self.env['account.payment.register'].with_context(active_model='account.move', active_ids=order.invoice_ids.ids).create({
                            'group_payment': True,
                        })._create_payments()
        return res