from odoo import models, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    branch_id = fields.Many2one('res.branch', string='Branch')
