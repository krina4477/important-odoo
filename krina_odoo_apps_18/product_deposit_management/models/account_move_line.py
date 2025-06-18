from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sequence = fields.Integer(string="Sequence", default=0)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if 'sequence' not in vals or vals['sequence'] == 0:
    #             vals['sequence'] = self.env['account.move.line'].search([], order='sequence desc', limit=1).sequence + 1
    #     return super().create(vals_list)



