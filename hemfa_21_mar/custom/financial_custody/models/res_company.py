from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    custody_account_id = fields.Many2one('account.account', string="Custody Account (Permanent)")
    custody_account_temp_id = fields.Many2one('account.account', string="Custody Account (Temporary)")
    custody_recompensation_percentage = fields.Float(string="Custody Recompensation Percentage", default=50.0)

    @api.constrains('custody_recompensation_percentage')
    def _check_percentage(self):
        for record in self:
            percentage = round(record.custody_recompensation_percentage, 2)
            if percentage < 0 or percentage > 100:
                raise ValidationError("The Custody Recompensation Percentage must be between 0 and 100.")
