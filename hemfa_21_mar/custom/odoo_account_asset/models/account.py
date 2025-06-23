# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    asset_depreciation_ids = fields.One2many('account.asset.depreciation.line.custom', 'move_id', string='Assets Depreciation Lines', ondelete="restrict")

#    @api.multi
#    def button_cancel(self):
#        for move in self:
#            for line in move.asset_depreciation_ids:
#                line.move_posted_check = False
#        return super(AccountMove, self).button_cancel()

#    @api.multi
#    def post(self, invoice=False):
    def _post(self, soft=True):
        for move in self:
            for depreciation_line in move.asset_depreciation_ids:
                depreciation_line.post_lines_and_close_asset()
#        return super(AccountMove, self).post(invoice=invoice)
        return super(AccountMove, self)._post(soft=soft)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    custom_asset_id = fields.Many2one(
        'account.asset.asset.custom',
        string='Asset',
        copy=False,
    )
