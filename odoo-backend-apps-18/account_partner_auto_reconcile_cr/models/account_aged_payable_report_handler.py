# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import models,api,fields,_

def isInt(value):
  try:
    int(value)
    return True
  except ValueError:
    return False


class ReportAccountAgedPayable(models.AbstractModel):
    _inherit = "account.aged.payable.report.handler"

    def _custom_options_initializer(self, report, options, previous_options=None):
        super()._custom_options_initializer(report, options, previous_options=previous_options)
        if self.env.user.has_group('account.group_account_user') and self.env.user.company_id.account_aged_payable_auto_reconcile:
            options['buttons'].append({'name': _('Auto Reconcile'), 'action': 'partner_auto_reconcile_aged_payable', 'sequence': 22})

    def partner_auto_reconcile_aged_payable(self, options):
        res = self.env['account.report'].browse(options.get('report_id'))
        all_lines = res._get_lines(options, None)
        partner_list = []

        for line in all_lines:
            p_id = str(line.get('id')) if isinstance(line.get('id'), str) else str(line.get('parent_id'))
            partner_val = p_id.split('~')

            if line.get('id') and ('partner_id~' in p_id or'"groupby": "partner_id"' in p_id) and len(partner_val) >= 3:
                if isInt(partner_val[6]) and partner_val[6] not in partner_list:
                    partner_list.append(partner_val[6])

        for partner in partner_list:
            move_domain = [
                ('display_type', 'not in', ('line_section', 'line_note')),
                ('partner_id', '=', int(partner)),
                ('parent_state', '=', 'posted'),
                ('account_id.account_type', '=', 'liability_payable'),
                ('account_id.non_trade', '=', False)
            ]

            account_move_line_data = self.env['account.move.line'].search(move_domain)

            wizard = self.env['account.reconcile.wizard'].with_context(
                active_model='account.move.line',
                active_ids=account_move_line_data.ids,
            ).new({})
            if wizard.is_write_off_required:
                wizard._action_open_wizard()
            else:
                wizard.reconcile()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
