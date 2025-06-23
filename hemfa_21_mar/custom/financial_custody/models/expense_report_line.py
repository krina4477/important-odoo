from odoo import models, fields

class ExpenseReportLine(models.Model):
    _name = 'financial.custody.expense.report.line'
    _description = 'Expense Report Line'

    expense_report_id = fields.Many2one('financial.custody.expense.report', string="Expense Report", ondelete='cascade')
    expense_account_id = fields.Many2one('account.account', string="Expense Account", required=True)
    partner_id = fields.Many2one('res.partner', string="Partner")
    reference = fields.Char(string="Reference")
    analytic_distribution = fields.Json(string="Analytic Distribution")
    analytic_precision = fields.Integer(string="Analytic Precision", default=2)
    amount = fields.Float(string="Amount", required=True)
    cash_request_id = fields.Many2one('financial.custody.request', string="Cash Request", ondelete='cascade')
