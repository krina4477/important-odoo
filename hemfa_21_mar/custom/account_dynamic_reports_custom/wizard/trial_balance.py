from odoo import api, fields, models, _


class InsTrialBalance(models.TransientModel):
    _inherit = "ins.trial.balance"

    def process_data(self, data):
        if data:
            cr = self.env.cr
            WHERE = '(1=1)'

            if data.get('journal_ids', []):
                WHERE += ' AND j.id IN %s' % str(tuple(data.get('journal_ids')) + tuple([0]))

            if data.get('account_ids', []):
                WHERE += ' AND a.id IN %s' % str(tuple(data.get('account_ids')) + tuple([0]))

            if data.get('analytic_ids', []):
                WHERE += ' AND anl.id IN %s' % str(tuple(data.get('analytic_ids')) + tuple([0]))
            if data.get('company_id', False):
                WHERE += ' AND l.company_id = %s' % data.get('company_id')

            if data.get('target_moves') == 'posted_only':
                WHERE += " AND m.state = 'posted'"

            if data.get('analytic_distribution_ids', []):
                WHERE += ' AND line_analytic.analytic_distribution_id IN %s' % str(
                    tuple(data.get('analytic_distribution_ids')) + tuple([0]))
            if self.branch_ids:
                if data.get('branch_ids', []):
                    WHERE += ' AND m.branch_id IN %s' % str(tuple(data.get('branch_ids')) + tuple([0]))

            if data.get('account_ids'):
                account_ids = self.env['account.account'].browse(data.get('account_ids'))
            else:
                account_ids = self.env['account.account'].search([('company_id', '=', data.get('company_id'))])
            company_currency_id = self.env.company.currency_id

            move_lines = {x.code: {'name': x.name, 'code': x.code, 'id': x.id,
                                   'initial_debit': 0.0, 'initial_credit': 0.0, 'initial_balance': 0.0,
                                   'debit': 0.0, 'credit': 0.0, 'balance': 0.0,
                                   'ending_credit': 0.0, 'ending_debit': 0.0, 'ending_balance': 0.0,
                                   'company_currency_id': company_currency_id.id} for x in
                          account_ids}  # base for accounts to display
            retained = {}
            retained_earnings = 0.0
            retained_credit = 0.0
            retained_debit = 0.0
            total_deb = 0.0
            total_cre = 0.0
            total_bln = 0.0
            total_init_deb = 0.0
            total_init_cre = 0.0
            total_init_bal = 0.0
            total_end_deb = 0.0
            total_end_cre = 0.0
            total_end_bal = 0.0
            for account in account_ids:
                currency = account.company_id.currency_id or self.env.company.currency_id
                WHERE_INIT = WHERE + " AND l.date < '%s'" % data.get('date_from')
                WHERE_INIT += " AND l.account_id = %s" % account.id
                init_blns = 0.0
                deb = 0.0
                cre = 0.0
                end_blns = 0.0
                end_cr = 0.0
                end_dr = 0.0
                if self.branch_ids:
                    sql = ('''
                        SELECT 
                            COALESCE(SUM(l.debit),0) AS initial_debit,
                            COALESCE(SUM(l.credit),0) AS initial_credit,
                            COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit),0) AS initial_balance
                        FROM account_move_line l
                        JOIN account_move m ON (l.move_id=m.id)
                        JOIN account_account a ON (l.account_id=a.id)
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)
                        JOIN account_journal j ON (l.journal_id=j.id)
                        JOIN res_branch b ON (l.branch_id=b.id)
                        LEFT JOIN move_line_analytic_distribution_rel line_analytic on (l.id = line_analytic.line_id)
                        WHERE %s
                    ''') % WHERE_INIT
                else:
                    sql = ('''
                                            SELECT 
                                                COALESCE(SUM(l.debit),0) AS initial_debit,
                                                COALESCE(SUM(l.credit),0) AS initial_credit,
                                                COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit),0) AS initial_balance
                                            FROM account_move_line l
                                            JOIN account_move m ON (l.move_id=m.id)
                                            JOIN account_account a ON (l.account_id=a.id)
                                            LEFT JOIN res_currency c ON (l.currency_id=c.id)
                                            LEFT JOIN res_partner p ON (l.partner_id=p.id)
                                            JOIN account_journal j ON (l.journal_id=j.id)
                                            LEFT JOIN move_line_analytic_distribution_rel line_analytic on (l.id = line_analytic.line_id)
                                            WHERE %s
                                        ''') % WHERE_INIT

                cr.execute(sql)
                init_blns = cr.dictfetchone()

                income_type_list = ['income', 'expense', 'income_other', 'expense_depreciation', 'expense_direct_cost']
                move_lines[account.code]['initial_balance'] = init_blns[
                    'initial_balance'] if account.account_type not in income_type_list else 0
                move_lines[account.code]['initial_debit'] = init_blns[
                    'initial_debit'] if account.account_type not in income_type_list else 0
                move_lines[account.code]['initial_credit'] = init_blns[
                    'initial_credit'] if account.account_type not in income_type_list else 0

                if account.account_type in [
                    'asset_receivable',
                    'asset_cash',
                    'asset_current',
                    'asset_non_current',
                    'asset_prepayments',
                    'asset_fixed',
                    'liability_payable',
                    'liability_credit_card',
                    'liability_current',
                    'liability_non_current',
                    'equity',
                    'equity_unaffected'] \
                        and self.strict_range:
                    move_lines[account.code]['initial_balance'] = 0.0
                    move_lines[account.code]['initial_debit'] = 0.0
                    move_lines[account.code]['initial_credit'] = 0.0
                    if self.strict_range and account.account_type != 'equity_unaffected':
                        retained_earnings += init_blns['initial_balance']
                        retained_credit += init_blns['initial_credit']
                        retained_debit += init_blns['initial_debit']
                total_init_deb += init_blns['initial_debit'] if account.account_type not in income_type_list else 0
                total_init_cre += init_blns['initial_credit'] if account.account_type not in income_type_list else 0
                total_init_bal += init_blns['initial_balance'] if account.account_type not in income_type_list else 0

                WHERE_CURRENT = WHERE + " AND l.date >= '%s'" % data.get(
                    'date_from') + " AND l.date <= '%s'" % data.get('date_to')
                WHERE_CURRENT += " AND a.id = %s" % account.id

                if self.branch_ids:
                    sql = ('''
                        SELECT
                            COALESCE(SUM(l.debit),0) AS debit,
                            COALESCE(SUM(l.credit),0) AS credit,
                            COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit),0) AS balance
                        FROM account_move_line l
                        JOIN account_move m ON (l.move_id=m.id)
                        JOIN account_account a ON (l.account_id=a.id)
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)
                        JOIN account_journal j ON (l.journal_id=j.id)
                        JOIN res_branch b ON (l.branch_id=b.id)
                        LEFT JOIN move_line_analytic_distribution_rel line_analytic on (l.id = line_analytic.line_id)
                        WHERE %s
                    ''') % WHERE_CURRENT
                else:
                    sql = ('''
                                            SELECT
                                                COALESCE(SUM(l.debit),0) AS debit,
                                                COALESCE(SUM(l.credit),0) AS credit,
                                                COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit),0) AS balance
                                            FROM account_move_line l
                                            JOIN account_move m ON (l.move_id=m.id)
                                            JOIN account_account a ON (l.account_id=a.id)
                                            LEFT JOIN res_currency c ON (l.currency_id=c.id)
                                            LEFT JOIN res_partner p ON (l.partner_id=p.id)
                                            JOIN account_journal j ON (l.journal_id=j.id)
                                            LEFT JOIN move_line_analytic_distribution_rel line_analytic on (l.id = line_analytic.line_id)
                                            WHERE %s
                                        ''') % WHERE_CURRENT

                cr.execute(sql)
                op = cr.dictfetchone()
                deb = op['debit']
                cre = op['credit']
                bln = op['balance']
                move_lines[account.code]['debit'] = deb
                move_lines[account.code]['credit'] = cre
                move_lines[account.code]['balance'] = bln

                end_blns = init_blns['initial_balance'] + bln if account.account_type not in income_type_list else bln
                end_cr = init_blns['initial_credit'] + cre if account.account_type not in income_type_list else cre
                end_dr = init_blns['initial_debit'] + deb if account.account_type not in income_type_list else deb

                move_lines[account.code]['ending_balance'] = end_blns
                move_lines[account.code]['ending_credit'] = end_cr
                move_lines[account.code]['ending_debit'] = end_dr

                if data.get('balance_is_zero') and (end_blns or bln):
                    move_lines.pop(account.code)
                    continue

                if data.get('display_accounts') == 'balance_not_zero':
                    if end_blns:  # debit or credit exist
                        total_deb += deb
                        total_cre += cre
                        total_bln += bln
                    elif bln:
                        continue
                    else:
                        move_lines.pop(account.code)
                else:
                    total_deb += deb
                    total_cre += cre
                    total_bln += bln

            if self.strict_range:
                retained = {'RETAINED': {'name': 'Unallocated Earnings', 'code': '', 'id': 'RET',
                                         'initial_credit': company_currency_id.round(retained_credit),
                                         'initial_debit': company_currency_id.round(retained_debit),
                                         'initial_balance': company_currency_id.round(retained_earnings),
                                         'credit': 0.0, 'debit': 0.0, 'balance': 0.0,
                                         'ending_credit': company_currency_id.round(retained_credit),
                                         'ending_debit': company_currency_id.round(retained_debit),
                                         'ending_balance': company_currency_id.round(retained_earnings),
                                         'company_currency_id': company_currency_id.id}}
            subtotal = {'SUBTOTAL': {
                'name': 'Total',
                'code': '',
                'id': 'SUB',
                'initial_credit': company_currency_id.round(total_init_cre),
                'initial_debit': company_currency_id.round(total_init_deb),
                'initial_balance': company_currency_id.round(total_init_bal),
                'credit': company_currency_id.round(total_cre),
                'debit': company_currency_id.round(total_deb),
                'balance': company_currency_id.round(total_bln),
                'ending_credit': company_currency_id.round(total_init_cre + total_cre),
                'ending_debit': company_currency_id.round(total_init_deb + total_deb),
                'ending_balance': company_currency_id.round(total_init_bal + total_bln),
                'company_currency_id': company_currency_id.id}}

            if self.show_hierarchy:
                move_lines = self.prepare_hierarchy(move_lines)
            return [move_lines, retained, subtotal]
