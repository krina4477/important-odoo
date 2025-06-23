# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountFiscalyearClose(models.TransientModel):
    _name = 'account.fiscalyear.close'
    _description = "Fiscalyear Close"

    fy_id = fields.Many2one('account.fiscalyear', 'Fiscal Year to close', required=True,
                            help="Select a Fiscal year to close")
    journal_id = fields.Many2one('account.journal', 'Opening Entries Journal', required=True,
                                 domain="[('type','=','situation'), ('company_id', 'in', allowed_company_ids)]")
    report_name = fields.Char('Name of new entries', required=True, help="Give name of the new entries",
                              default="End of Fiscal Year Entry")

    def data_save(self):
        AccountMove = self.env['account.move']
        AccountMoveLine = self.env['account.move.line']
        AccountAccount = self.env['account.account']
        AccountPeriod = self.env['account.period']

        for data in self:
            fy_id = data.fy_id

            # Fetch periods for old fiscal year
            fy_periods = AccountPeriod.search([('fiscalyear_id', '=', fy_id.id)], order='date_stop desc')
            if not fy_periods:
                raise UserError(_('No periods found for the fiscal year to generate opening entries.'))

            if any(period.state == 'draft' for period in fy_periods):
                raise UserError(_('Close all open periods before proceeding.'))

            closing_date = fy_periods[0].date_stop
            opening_date = closing_date + timedelta(days=1)

            # Create the closing and opening moves
            def create_move(date, journal, ref):
                return AccountMove.with_context(skip_period_check=True).create({
                    'name': '/',
                    'ref': ref,
                    'date': date,
                    'journal_id': journal.id,
                })

            closing_move = create_move(closing_date, data.journal_id, data.report_name)
            opening_move = create_move(opening_date, data.journal_id, data.report_name)

            # Process accounts for the closing and opening moves
            def process_accounts():
                account_types = [
                    'income', 'income_other', 'expense',
                    'expense_depreciation', 'expense_direct_cost'
                ]
                accounts = AccountAccount.search([
                    ('account_type', 'in', account_types),
                    ('company_id', '=', data.journal_id.company_id.id),
                ])

                if not accounts:
                    return

                move_lines = AccountMoveLine.sudo().search([
                    ('account_id', 'in', accounts.ids),
                    ('period_id', 'in', fy_periods.ids),
                    ('parent_state', '=', 'posted'),
                ])

                total_balance = sum(line.balance for line in move_lines)
                if not total_balance:
                    return

                # Determine debit and credit values
                debit = total_balance if total_balance > 0 else 0
                credit = -total_balance if total_balance < 0 else 0

                # Fetch required accounts
                current_year_account = AccountAccount.search([('account_type', '=', 'equity_unaffected')], limit=1)
                if not current_year_account:
                    raise UserError(_('Please define a current year account.'))

                # Closing move lines
                closing_move.write({
                    'line_ids': [
                        (0, 0, {
                            'name': data.report_name,
                            'account_id': current_year_account.id,
                            'debit': credit,
                            'credit': debit,
                        }),
                        (0, 0, {
                            'name': data.report_name,
                            'account_id': data.journal_id.counter_part_account.id,
                            'debit': debit,
                            'credit': credit,
                        }),
                    ]
                })

                # Opening move lines
                opening_move.write({
                    'line_ids': [
                        (0, 0, {
                            'name': data.report_name,
                            'account_id': data.journal_id.counter_part_account.id,
                            'debit': credit,
                            'credit': debit,
                        }),
                        (0, 0, {
                            'name': data.report_name,
                            'account_id': data.journal_id.equity_account.id,
                            'debit': debit,
                            'credit': credit,
                        }),
                    ]
                })

            process_accounts()

            # Post the moves
            closing_move.action_post()
            opening_move.action_post()

            # Update fiscal year and lock date
            data.journal_id.company_id.sudo().write({
                'fiscalyear_lock_date': closing_date,
            })
            fy_id.write({'state': 'done'})

        return {'type': 'ir.actions.act_window_close'}
