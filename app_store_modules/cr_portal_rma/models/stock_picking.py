# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Picking(models.Model):
    _inherit = 'stock.picking'

    def _create_credit_note_on_return(self, so):
        """Automatically create a credit note when return is validated"""
        sale_order = so
        if not sale_order or not sale_order.invoice_ids:
            return

        # Get original invoice(s) related to this sale
        original_invoice = sale_order.invoice_ids.filtered(
            lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted')
        if not original_invoice:
            return

        # Prepare refund (credit note)
        refund = self.env['account.move'].with_context(default_move_type='out_refund').create({
            'partner_id': sale_order.partner_id.id,
            'invoice_origin': self.origin,
            'invoice_date': fields.Date.today(),
            'move_type': 'out_refund',
            'invoice_line_ids': [],
        })

        # Create refund lines based on returned products
        for move in self.move_ids_without_package:
            if move.product_id.invoice_policy != 'delivery':
                continue

            refund.invoice_line_ids += self.env['account.move.line'].create({
                'product_id': move.product_id.id,
                'quantity': move.quantity,
                'price_unit': move.product_id.lst_price,
                'name': f"Refund for return of {move.product_id.display_name}",
                'tax_ids': [(6, 0, move.product_id.taxes_id.ids)],
                'account_id': move.product_id.categ_id.property_account_income_categ_id.id,
                'move_id': refund.id
            })

        # refund._onchange_invoice_line_ids()
        refund.action_post()

    def button_validate(self):
        res = super().button_validate()
        print("RESSSSSSSSSSSSSSSSS",self)
        if self.state == 'done':
            return_doc = self.env['order.return'].sudo().search([('return_picking_id', '=', self.id)])
            if return_doc:
                return_doc.state = 'done'
                so = return_doc.website_order_id

                for picking in self:
                    if picking.picking_type_code == 'incoming' and picking.origin:
                        # Possibly a return picking – you can refine this further if needed
                        picking._create_credit_note_on_return(so)
        return res