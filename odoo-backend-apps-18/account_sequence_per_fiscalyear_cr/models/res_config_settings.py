# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    seq_per_fiscalyear = fields.Boolean(string='Generate Sequence Per Fiscal Year', implied_group='account_accountant.group_fiscal_year')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['seq_per_fiscalyear'] = self.env['ir.config_parameter'].sudo().get_param(
            'account_sequence_per_fiscalyear_cr.seq_per_fiscalyear', default=False)
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('account_sequence_per_fiscalyear_cr.seq_per_fiscalyear',
                                                         self.seq_per_fiscalyear)
        super(ResConfigSettings, self).set_values()
