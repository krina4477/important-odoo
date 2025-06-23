from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ExpenseExchangeRate(models.Model):
    _inherit = 'expense.model'

    exchange_rate = fields.Float(string="Exchange Rate", default=1.0, help="Enter manual exchange rate if different from the system rate", digits=(12, 6))
    amount_in_currency = fields.Monetary(string="Amount in Currency", compute="_compute_amount_in_currency", store=True, currency_field="currency_id")
    different_currency = fields.Boolean(string="Different Currency", compute="_compute_different_currency", store=True, help="Check if the journal currency is different from the company currency.")

    @api.depends('journal_id')
    def _compute_different_currency(self):
        """ Compute if the journal's currency differs from the company's currency. """
        for record in self:
            record.different_currency = bool(record.journal_id.currency_id and record.journal_id.currency_id != record.company_id.currency_id)
            if not record.different_currency:
                record.exchange_rate = 1.0  # Reset exchange rate when same currency is selected.

    @api.depends('total_amount', 'exchange_rate')
    def _compute_amount_in_currency(self):
        """ Compute the amount in the selected currency based on the manual exchange rate. """
        for record in self:
            record.amount_in_currency = record.total_amount * record.exchange_rate

    def _prepare_move_vals_with_exchange_rate(self):
        """ Prepare move values considering the exchange rate if a different currency is used. """
        move_vals = super(ExpenseExchangeRate, self)._prepare_move_vals()

        # Apply exchange rate to amounts in line items
        for line in move_vals.get('line_ids', []):
            debit = line[2].get('debit', 0.0)
            credit = line[2].get('credit', 0.0)
            branch_id = self.line_ids.filtered(lambda l: l.account_id.id == line[2]['account_id']).branch_id.id

            # If using different currency, convert debit/credit based on exchange rate
            if self.different_currency:
                if debit:
                    line[2]['debit'] = debit * self.exchange_rate
                if credit:
                    line[2]['credit'] = credit * self.exchange_rate
                line[2]['amount_currency'] = debit if debit else -credit  # Store the amount in the journal's currency
                line[2]['currency_id'] = self.journal_id.currency_id.id
            else:
                # Ensure currency_id is not set when the currency is the same
                line[2]['currency_id'] = False

            # Add branch_id to the line
            line[2]['branch_id'] = branch_id or self.branch_id.id

        return move_vals

    def _prepare_move_vals(self):
        """ Override to include the logic for applying the exchange rate if applicable. """
        # Ensure that only accounts compatible with the journal's currency are selected
        for line in self.line_ids:
            if line.account_id.currency_id and line.account_id.currency_id != self.journal_id.currency_id:
                continue

        # If the journal currency is different, apply the exchange rate logic
        if self.different_currency:
            return self._prepare_move_vals_with_exchange_rate()

        return super(ExpenseExchangeRate, self)._prepare_move_vals()

    @api.model
    def create(self, vals):
        """Override to bypass the currency validation Odoo imposes."""
        self = self.with_context(check_move_validity=False)
        return super(ExpenseExchangeRate, self).create(vals)

    def write(self, vals):
        """Override to bypass the currency validation Odoo imposes."""
        self = self.with_context(check_move_validity=False)
        return super(ExpenseExchangeRate, self).write(vals)
