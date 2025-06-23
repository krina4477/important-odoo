from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError  # Import ValidationError
import logging

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_cash_request_related = fields.Boolean(string="Cash Request Related", default=False)
    
    def button_draft(self):
        # Check if the reset is coming from either Cash Request or Reconciliation Cash Request
        if self.is_cash_request_related and not self.env.context.get('from_cash_request', False):
            raise UserError(_("You cannot reset this journal entry to draft directly. "
                              "Please contact your manager or reset through the Cash Request process."))
        
        # If reset is allowed, proceed with resetting the journal entry to draft
        return super(AccountMove, self).button_draft()

    def action_post(self):
        # Check if the posting is coming from the Cash Request context
        if self.is_cash_request_related and not self.env.context.get('from_cash_request', False):
            raise UserError(_("You cannot post this journal entry directly. Please post it through the Cash Request process."))
        
        # If posting is allowed, proceed with posting the journal entry
        return super(AccountMove, self).action_post()

    def button_cancel(self):
        if self.is_cash_request_related and not self.env.context.get('from_cash_request', False):
            raise UserError(_("You cannot cancel this journal entry directly. "
                              "Please cancel it through the Cash Request process."))
        return super(AccountMove, self).button_cancel()