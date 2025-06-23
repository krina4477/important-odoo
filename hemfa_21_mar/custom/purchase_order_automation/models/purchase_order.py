from odoo import api, fields, models, exceptions


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        print("[[[[[[[[[[[[[[[[[[[[[[s;ss;s;s;;s]]]]]]]]]]]]]]]]]]]]]]")
        for order in self:
            company_id = order.company_id
            if company_id.is_po_delivery_set_to_done and order.picking_ids: 
                for picking in self.picking_ids:
                    if picking.state == 'cancel':
                        continue
                    picking.immediate_transfer = True
                    for move in picking.move_ids.mapped('move_line_ids'):
                        move.qty_done = move.reserved_qty or move.reserved_uom_qty
                    picking._autoconfirm_picking()
                    picking.action_set_quantities_to_reservation()
                    picking.action_confirm()
                    for move_line in picking.move_ids_without_package:
                        move_line.quantity_done = move_line.product_uom_qty

                    for mv_line in picking.move_ids.mapped('move_line_ids'):
                        mv_line.qty_done = mv_line.reserved_qty or mv_line.reserved_uom_qty
                    picking._action_done()
            else:
                for picking in self.picking_ids:
                    if picking.state == 'cancel':
                        continue
                    picking.immediate_transfer = False

                    

            if company_id.create_invoice_for_po and not order.invoice_ids:
                # journal = journal_obj.search([('type', '=', 'purchase')],limit=1)
                # invoice_id = invoice_obj.new({'purchase_id': order.id, 'partner_id':order.partner_id.id, 'move_type': 'in_invoice', 'journal_id': journal.id})
                # invoice_id.purchase_id = order
                # invoice_id.with_context(create_bill=True)._onchange_purchase_auto_complete()
                # invoice_id._onchange_partner_id()
                # invoice_id._onchange_invoice_line_ids()
                order.action_create_invoice()
                # order.invoice_ids = invoice_id
                for line in order.invoice_ids.mapped('line_ids').filtered(lambda inv_line: inv_line.product_id.type == 'service' ):
                    line.with_context(check_move_validity = False).quantity = line.purchase_line_id.product_qty

            if company_id.validate_po_invoice and order.invoice_ids:
                for invoice in order.invoice_ids:
                    invoice.invoice_date = fields.Date.today()
                    invoice.action_post()
            
        return res  
