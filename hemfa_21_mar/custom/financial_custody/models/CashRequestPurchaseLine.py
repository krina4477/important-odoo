from odoo import models, fields, api, _
from odoo.exceptions import ValidationError  # Import ValidationError

class CashRequestPurchaseLine(models.Model):
    _name = 'financial.custody.purchase.line'
    _description = 'Cash Request Purchase Line'

    cash_request_id = fields.Many2one('financial.custody.request', string="Cash Request", ondelete='cascade')
    bill_id = fields.Many2one('account.move', string="Bill", domain=[('move_type', '=', 'in_invoice'), ('amount_residual', '>', 0), ('state', '=', 'posted')], required=True)
    partner_id = fields.Many2one(related='bill_id.partner_id', string="Vendor", readonly=True)  # Vendor
    purchase_id = fields.Many2one('purchase.order', string="PO Number", compute='_compute_purchase_id', store=True)
    currency_id = fields.Many2one('res.currency', related='bill_id.currency_id', string="Currency", readonly=True)  # Add currency field
    total_amount = fields.Monetary(related='bill_id.amount_total', string="Total Amount", readonly=True, currency_field='currency_id')
    amount_due = fields.Monetary(related='bill_id.amount_residual', string="Amount Due", readonly=True, currency_field='currency_id')
    amount_to_pay = fields.Monetary(string="Amount to Pay", currency_field='currency_id')

    @api.depends('bill_id')
    def _compute_purchase_id(self):
        for line in self:
            # Check if the bill has a linked PO and set the purchase_id
            if line.bill_id and line.bill_id.invoice_origin:
                purchase_order = self.env['purchase.order'].search([('name', '=', line.bill_id.invoice_origin)], limit=1)
                line.purchase_id = purchase_order.id if purchase_order else False
            else:
                line.purchase_id = False

    @api.constrains('amount_to_pay')
    def _check_amount_to_pay(self):
        for line in self:
            if line.amount_to_pay > line.amount_due:
                raise ValidationError(_("The amount to pay cannot be greater than the amount due."))