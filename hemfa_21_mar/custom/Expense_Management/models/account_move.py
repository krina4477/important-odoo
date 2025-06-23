from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_draft(self):
        """Extend the standard 'button_draft' method to set the linked expense to 'draft'"""
        res = super(AccountMove, self).button_draft()

        # Search for related expenses that are linked to this journal entry
        expenses = self.env['expense.model'].search([('move_id', 'in', self.ids), ('state', '=', 'confirmed')])
        for expense in expenses:
            expense.action_set_to_draft()

        return res
