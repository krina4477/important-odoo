# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    #Fully Override to pass discount things to the vendor bill
    def _create_po_from_so(self, company):
        print("_create_po_from_so", self)
        company_partner_id = self.env['res.company'].search([('partner_id', '=', self.partner_id.id)])
        current_company_id = self.env.company
        purchase_order = self.env['purchase.order']
        purchase_order_line = self.env['purchase.order.line']
        picking_validate = False
        create_invoice = False
        validate_invoice = False
        bill_id = False
        line_lot = []
        # ---------------- Create PO

        po_vals = self.sudo().get_po_values(company_partner_id, current_company_id)
        print("~~~~~~~~~~~po_vals", po_vals)
        po_id = purchase_order.sudo().create(po_vals)
        # ---------------- END Create PO
        for line in self.order_line:
            if line.product_id.tracking != 'none':
                line_lot.append(line.product_id)
            po_line_vals = self.sudo().get_po_line_data(po_id.id, company_partner_id, line)
            purchase_order_line.sudo().create(po_line_vals)
        if not self.client_order_ref:
            self.client_order_ref = po_id.name
        po_id.sudo().button_confirm()
        setting_id = self.env.user.company_id
        if setting_id.validate_picking:
            sequence_number = 1
            for receipt in po_id.picking_ids:
                for move in receipt.move_ids_without_package:
                    # move.write({'quantity_done':move.product_uom_qty})
                    # below code for adding auto serial number in picking
                    prefix = ''
                    if move.product_id.tracking == 'serial':
                        prefix = 'SN'
                    elif move.product_id.tracking == 'lot':
                        prefix = 'LT'
                    elif move.product_id.tracking == 'none':
                        move.write({'quantity_done': move.product_uom_qty})

                    if prefix:
                        if move.product_id.tracking != 'none':
                            move_qty = move.product_uom_qty
                            for i in range(int(move_qty)):
                                lot_id = '{0}-{1:04d}'.format(prefix, sequence_number)
                                existing_lot = move.env['stock.lot'].sudo().search([('name', '=', lot_id)])
                                while existing_lot:
                                    sequence_number += 1
                                    lot_id = '{0}-{1:04d}'.format(prefix, sequence_number)
                                    existing_lot = move.env['stock.lot'].sudo().search([('name', '=', lot_id)])
                                lot_name = move.env['stock.lot'].sudo().create({
                                    'name': lot_id,
                                    'product_id': move.product_id.id,
                                    'company_id': move.company_id.id,
                                    'ref': lot_id,
                                })
                                move.env['stock.move.line'].sudo().create({
                                    'move_id': move.id,
                                    'product_id': move.product_id.id,
                                    'product_uom_id': move.product_uom.id,
                                    'lot_id': lot_name.id,
                                    'location_id': move.location_id.id,
                                    'location_dest_id': move.location_dest_id.id,
                                    'qty_done': 1,
                                })
                                sequence_number += 1
                                move_qty -= 1
                    # ===============================
                if not line_lot:
                    receipt.sudo()._action_done()
                else:
                    receipt.sudo()._action_done()
                if receipt.state == 'done':
                    picking_validate = True
        """
            Create Invoice
        """
        if True or setting_id.create_invoice:
            if True or setting_id.create_invoice == True:
                invoice_object = self.env['account.move']
                invoice_line_obj = self.env['account.move.line']
                journal = self.env['account.journal'].sudo().search(
                    [('type', '=', 'purchase'), ('company_id', '=', company.id)], limit=1)
                internal_id = self.env['inter.transfer.company']
                inter_transfer_lines = self.env['inter.transfer.company.line']
                ctx = dict(self._context or {})
                ctx.update({
                    'move_type': 'in_invoice',
                    'default_purchase_id': po_id.id,
                    'default_currency_id': po_id.currency_id.id,
                    'default_origin': po_id.name,
                    'default_reference': po_id.name,
                    'current_company_id': current_company_id.id,
                    'company_partner_id': company_partner_id.id
                })
                bill_id = invoice_object.with_context(
                    create_bill=True
                ).sudo().with_company(company).create({
                    'partner_id': po_id.partner_id.id,
                    'currency_id': po_id.currency_id.id,
                    'company_id': po_id.company_id.id,
                    'move_type': 'in_invoice',
                    #  'journal_id':journal.id,
                    'manual_currency_rate': po_id.purchase_manual_currency_rate,
                    'manual_currency_rate_active': po_id.purchase_manual_currency_rate_active,
                    'purchase_vendor_bill_id': po_id.id,
                    'purchase_id': po_id.id,
                    'ref': po_id.name,
                    'discount_type': self.discount_type,
                    'discount_method': self.discount_method,
                    'discount_amount': self.discount_amount
                })

                new_lines = self.env['account.move.line']
                new_lines = []
                for line in po_id.order_line.filtered(lambda l: not l.display_type):
                    new_lines.append((
                        0, 0, line._prepare_account_move_line(bill_id)
                    ))
                bill_id.write({
                    'invoice_line_ids': new_lines,
                    'purchase_id': False,
                    'invoice_date': bill_id.date
                })
                bill_id.invoice_payment_term_id = po_id.payment_term_id
                bill_id.invoice_origin = ', '.join(po_id.mapped('name'))
                bill_id.ref = ', '.join(po_id.filtered('partner_ref').mapped('partner_ref')) or bill_id.reference
        if True or setting_id.validate_invoice:
            print("company", company)
            if bill_id:
                bill_id.sudo().with_company(company)._post()
            else:
                raise ValidationError(_('Please First give access to Create invoice.'))

        if self.internal_id.id:
            if po_id.id:
                if not self.internal_id.to_warehouse.id:
                    self.internal_id.update({
                        'purchase_id': po_id.id or False,
                        'currency_id': po_id.currency_id.id or False,
                        'to_warehouse': company_partner_id.intercompany_warehouse_id.id
                    })
                else:
                    self.internal_id.update({
                        'purchase_id': po_id.id or False,
                        'currency_id': po_id.currency_id.id or False,
                    })
            if bill_id:
                bill_details = []
                bill_details.append(bill_id.id)
                if len(self.internal_id.invoice_id) > 0:
                    for inv in self.internal_id.invoice_id:
                        bill_details.append(inv.id)
                self.internal_id.update({
                    'invoice_id': [(6, 0, bill_details)],
                })
        if not po_id.internal_id.id:
            po_id.internal_id = self.internal_id.id
        return po_id


    def get_po_line_data(self, po_id, company, line):
        vals = super(SaleOrder, self).get_po_line_data(po_id, company, line)
        vals.update({
            'discount_method': line.discount_method,
            'discount_amount': line.discount_amount,
        })
        return vals

    def get_po_values(self, company_partner_id, current_company_id):
        res = super(SaleOrder, self).get_po_values(company_partner_id, current_company_id)
        res.update({
            'discount_type': self.discount_type,
            'discount_method': self.discount_method,
            'discount_amount': self.discount_amount
        })
        return res
