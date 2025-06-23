from odoo import models, fields, api

class ExpenseReport(models.Model):
    _name = 'financial.custody.expense.report'
    _description = 'Expense Report for Custody Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Fields
    name = fields.Char(string="Report Reference", required=True, copy=False, readonly=True, default='New', tracking=True)
    cash_request_id = fields.Many2one('financial.custody.request', string="Cash Request", required=True, ondelete='cascade', tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Requested By", related='cash_request_id.employee_id', store=True, readonly=True)
    description = fields.Text(string="Description", related='cash_request_id.description', store=True, readonly=True)
    
    total_expense = fields.Float(string="Total Expense", compute='_compute_total_expense', store=True)
    
    expense_line_ids = fields.One2many('financial.custody.expense.report.line', 'expense_report_id', string="Expense Lines", tracking=True)
    custody_account_id = fields.Many2one('account.account', string="Custody Account", related='cash_request_id.custody_account_id', store=True, readonly=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('reconciled', 'Reconciled')
    ], default='draft', tracking=True)

    @api.depends('expense_line_ids', 'expense_line_ids.amount')
    def _compute_total_expense(self):
        for record in self:
            total = sum(line.amount for line in record.expense_line_ids)
            record.total_expense = total if total else 0.0  # Ensuring no empty values

    def action_submit(self):
        self.write({'state': 'submitted'})
        self.cash_request_id.message_post(body="Expense Report Submitted.")
