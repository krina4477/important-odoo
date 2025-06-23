# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import api, Command, fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMove, self).create(vals_list)
        msg = str(len(res)) + ' ' + 'Move Created.'
        self.env.user.notify_info(title='Invoice',id=res.id,message=msg)
        return res