from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ExpenseModel(models.Model):
    _name = 'expense.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Expense Model'

    name = fields.Char(string="Reference", required=True, default=lambda self: self.env['ir.sequence'].next_by_code('expense.model'), tracking=True)
    type = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')], string="Type", required=True, tracking=True)
    journal_id = fields.Many2one('account.journal', string="Journal", required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string="Currency", compute="_compute_currency", store=True)
    company_currency_id = fields.Many2one('res.currency', string="Company Currency", related='company_id.currency_id', readonly=True)
    date = fields.Date(string="Date", default=fields.Date.today, tracking=True)
    line_ids = fields.One2many('expense.line.model', 'expense_id', string="Expense Lines")
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount", store=True, currency_field="company_currency_id")
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    account_ids = fields.Many2many('account.account', string="Expense Accounts", compute="_compute_account_ids", store=True)
    move_id = fields.Many2one('account.move', string="Journal Entry", readonly=True)
    exchange_rate = fields.Float(string="Exchange Rate", default=1.0, help="Manual exchange rate", digits=(12, 6))
    branch_id = fields.Many2one('res.branch', string="Branch", required=True, tracking=True, default=lambda self: self.env.user.branch_id.id)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled')
    ], string="Status", default='draft', tracking=True)

    approver_id = fields.Many2one('res.users', string="Approved By", readonly=True, tracking=True)

    @api.depends('journal_id')
    def _compute_currency(self):
        """Compute the currency based on the journal or default to company currency."""
        for record in self:
            record.currency_id = record.journal_id.currency_id or record.company_id.currency_id

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        """Compute the total amount based on the expense lines."""
        for record in self:
            record.total_amount = sum(line.amount for line in record.line_ids)

    @api.depends('line_ids.account_id')
    def _compute_account_ids(self):
        """Compute the accounts used in the expense lines."""
        for record in self:
            accounts = record.line_ids.mapped('account_id')
            record.account_ids = [(6, 0, accounts.ids)]

    @api.onchange('type')
    def _onchange_type(self):
        """Apply a domain filter for journal selection based on type."""
        return {'domain': {'journal_id': [('type', '=', self.type)]}}

    def _prepare_move_vals(self):
        """Prepare move values with exchange rates for journals in different currencies."""
        move_vals = {
            'ref': self.name,
            'date': self.date,
            'journal_id': self.journal_id.id,
            'line_ids': [],
        }

        for line in self.line_ids:
            debit_in_company_currency = line.amount
            credit_in_company_currency = 0.0

            if self.journal_id.currency_id and self.journal_id.currency_id != self.company_id.currency_id:
                debit_in_journal_currency = line.amount * self.exchange_rate
                move_vals['line_ids'].append((0, 0, {
                    'account_id': line.account_id.id,
                    'branch_id': line.branch_id.id,
                    'name': line.reference,
                    'partner_id': line.partner_id.id,
                    'debit': debit_in_company_currency,
                    'credit': credit_in_company_currency,
                    'amount_currency': debit_in_journal_currency,
                    'currency_id': self.journal_id.currency_id.id,
                    'analytic_distribution': line.analytic_distribution,
                    'analytic_precision': self.env['decimal.precision'].precision_get('Account'),
                }))
            else:
                # For same currency, do not set currency_id or amount_currency
                move_vals['line_ids'].append((0, 0, {
                    'account_id': line.account_id.id,
                    'branch_id': line.branch_id.id,
                    'name': line.reference,
                    'partner_id': line.partner_id.id,
                    'debit': debit_in_company_currency,
                    'credit': credit_in_company_currency,
                    'analytic_distribution': line.analytic_distribution,
                    'analytic_precision': self.env['decimal.precision'].precision_get('Account'),
                    
                }))

        # Add balancing line for the journal's default account
        move_vals['line_ids'].append((0, 0, {
            'account_id': self.journal_id.default_account_id.id,
            'branch_id': self.branch_id.id,
            'name': _('Expense Journal Entry'),
            'debit': 0.0,
            'credit': self.total_amount,
            
        }))

        return move_vals

    def action_confirm(self):
        """Confirm the expense and post the related journal entry."""
        if not self.line_ids:
            raise UserError(_('Please add at least one expense line.'))

        move_vals = self._prepare_move_vals()

        if not self.move_id:
            self.move_id = self.env['account.move'].create(move_vals)
        else:
            self.move_id.line_ids.unlink()
            self.move_id.write(move_vals)

        if self.move_id.state != 'posted':
            self.move_id.action_post()

        self.state = 'confirmed'

    def action_set_to_draft(self):
        """Set the expense and related journal entry to draft."""
        if self.move_id and self.move_id.state == 'posted':
            self.move_id.button_draft()
        self.state = 'draft'

    @api.depends('move_id.state')
    def _check_journal_state(self):
        """Ensure the expense status is 'Draft' when the journal entry is set to draft."""
        for expense in self:
            if expense.move_id and expense.move_id.state == 'draft' and expense.state == 'confirmed':
                expense.state = 'draft'

    def action_submit(self):
        """Submit the expense for approval."""
        if not self.line_ids:
            raise UserError(_('Please add at least one expense line.'))
        self.state = 'submitted'

        approver_group = self.env.ref('Expense_Management.group_expense_approver')
        manager_group = self.env.ref('Expense_Management.group_expense_manager')

        approvers = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
        managers = self.env['res.users'].search([('groups_id', 'in', manager_group.id)])

        users_to_notify = approvers | managers

        for user in users_to_notify:
            self.activity_schedule('mail.mail_activity_data_todo', user_id=user.id, summary=_("New Expense Submitted for Approval"), note=_("Expense %s has been submitted for approval." % (self.name)))

    def action_approve(self):
        """Approve the expense."""
        if self.state != 'submitted':
            raise UserError(_('Expense must be submitted first.'))
        self.approver_id = self.env.user
        self.state = 'approved'

    def action_cancel(self):
        """Cancel the expense."""
        if self.state == 'approved':
            raise UserError(_('You cannot cancel an approved expense.'))
        self.state = 'canceled'

    def unlink(self):
        """Delete the expense only if it is in draft state."""
        for expense in self:
            if expense.state == 'confirmed':
                raise UserError(_('You cannot delete a confirmed expense. Set it to draft first.'))
            if expense.move_id and expense.move_id.state == 'draft':
                expense.move_id.unlink()
        return super(ExpenseModel, self).unlink()

    def get_expense_by_journal(self):
        """Get the expense amount grouped by journal."""
        return self.read_group(
            [('state', '=', 'confirmed')],
            ['journal_id', 'total_amount:sum'],
            ['journal_id']
        )

    def action_view_journal_entry(self):
        """Open the related journal entry."""
        self.ensure_one()
        if self.move_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Journal Entry'),
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': self.move_id.id,
                'target': 'current',
            }
        else:
            raise UserError(_('No journal entry found for this expense.'))


class ExpenseLineModel(models.Model):
    _name = 'expense.line.model'
    _description = 'Expense Line Model'

    expense_id = fields.Many2one('expense.model', string="Expense Reference", required=True, ondelete='cascade')
    account_id = fields.Many2one('account.account', string="Expense Account", required=True)
    reference = fields.Char(string="Reference")
    amount = fields.Float(string="Amount", required=True)
    analytic_distribution = fields.Json(string="Analytic Distribution", widget="analytic_distribution")
    analytic_precision = fields.Integer(string="Analytic Precision", default=2)
    partner_id = fields.Many2one('res.partner', string='Partner')
    branch_id = fields.Many2one('res.branch', string="Branch", required=True)
