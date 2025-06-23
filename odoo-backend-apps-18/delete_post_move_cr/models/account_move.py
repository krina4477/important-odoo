# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_remove(self):
        self.button_draft()
        self.unlink()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [
            ('move_type', '=', 'out_invoice'),
        ]
        action['context'] = {'default_move_type': 'out_invoice', 'move_type': 'out_invoice'}
        return action

    def button_remove_tree(self):
        self.button_draft()
        self.unlink()

