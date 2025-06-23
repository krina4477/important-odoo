from odoo import api, fields, models, _

FETCH_RANGE = 2000


class InsGeneralLedger(models.TransientModel):
    _inherit = "ins.general.ledger"

    def process_data(self):
        '''
        It is the method for showing summary details of each accounts. Just basic details to show up
        Three sections,
        1. Initial Balance
        2. Current Balance
        3. Final Balance
        :return:
        '''
        cr = self.env.cr

        data = self.get_filters(default_filters={})

        WHERE = self.build_where_clause(data)
        filter_currency_id = data.get('currency_ids')[0] if data.get('currency_ids') and len(
            data.get('currency_ids')) == 1 else False

        account_company_domain = [('company_id', '=', self.env.context.get('company_id') or self.env.company.id)]

        if data.get('account_tag_ids', []):
            account_company_domain.append(('tag_ids', 'in', data.get('account_tag_ids', [])))

        if data.get('account_ids', []):
            account_company_domain.append(('id', 'in', data.get('account_ids', [])))

        account_ids = self.env['account.account'].search(account_company_domain)

        move_lines = {
            x.code: {
                'name': x.name,
                'code': x.code,
                'company_currency_id': 0,
                'company_currency_symbol': 'AED',
                'company_currency_precision': 0.0100,
                'company_currency_position': 'after',
                'account_currency_id': filter_currency_id,
                'account_currency_symbol': x.currency_id.symbol,
                'id': x.id,
                'lines': []
            } for x in sorted(account_ids, key=lambda a: a.code)
        }
        for account in account_ids:

            currency = account.company_id.currency_id or self.env.company.currency_id
            symbol = currency.symbol
            rounding = currency.rounding
            position = currency.position

            opening_balance = 0

            WHERE_INIT = WHERE + " AND l.date < '%s'" % data.get('date_from')
            WHERE_INIT += " AND l.account_id = %s" % account.id
            if data.get('sort_accounts_by') == 'date':
                ORDER_BY_CURRENT = 'l.date, l.move_id'
            else:
                ORDER_BY_CURRENT = 'j.code, p.name, l.move_id'

            if not data.get('initial_balance'):
                if self.branch_ids:
                    sql = ('''
                        SELECT 
                            COALESCE(SUM(l.debit),0) AS debit, 
                            COALESCE(SUM(l.credit),0) AS credit, 
                            COALESCE(SUM(l.debit - l.credit),0) AS balance
                        FROM account_move_line l
                        JOIN account_move m ON (l.move_id=m.id)
                        JOIN account_account a ON (l.account_id=a.id)
                        --LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)
                        JOIN account_journal j ON (l.journal_id=j.id)
                        JOIN res_branch b ON (l.branch_id=b.id)
                        LEFT JOIN move_line_analytic_distribution_rel line_analytic on (line_analytic.line_id = l.id)
                        WHERE %s
                    ''') % WHERE_INIT
                else:
                    sql = ('''
                                           SELECT 
                                               COALESCE(SUM(l.debit),0) AS debit, 
                                               COALESCE(SUM(l.credit),0) AS credit, 
                                               COALESCE(SUM(l.debit - l.credit),0) AS balance
                                           FROM account_move_line l
                                           JOIN account_move m ON (l.move_id=m.id)
                                           JOIN account_account a ON (l.account_id=a.id)
                                           --LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                                           LEFT JOIN res_currency c ON (l.currency_id=c.id)
                                           LEFT JOIN res_partner p ON (l.partner_id=p.id)
                                           JOIN account_journal j ON (l.journal_id=j.id)
                                           LEFT JOIN move_line_analytic_distribution_rel line_analytic on (line_analytic.line_id = l.id)
                                           WHERE %s
                                       ''') % WHERE_INIT

                cr.execute(sql)
                for row in cr.dictfetchall():
                    row['move_name'] = 'Initial Balance'
                    row['account_id'] = account.id
                    row['initial_bal'] = True
                    row['ending_bal'] = False
                    opening_balance += row['balance']
                    move_lines[account.code]['lines'].append(row)
            WHERE_CURRENT = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                'date_to')
            WHERE_CURRENT += " AND a.id = %s" % account.id
            if self.branch_ids:
                sql = ('''
                    SELECT
                        l.id AS lid,
                        l.date AS ldate,
                        j.code AS lcode,
                        p.name AS partner_name,
                        m.name AS move_name,
                        l.name AS lname,
                        l.currency_id as lcurrency,
                        COALESCE(l.debit,0) AS debit,
                        COALESCE(l.credit,0) AS credit,
                        COALESCE(l.debit - l.credit,0) AS balance,
                        COALESCE(l.amount_currency,0) AS amount_currency
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    --LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    JOIN res_branch b ON (l.branch_id=b.id)
                    LEFT JOIN move_line_analytic_distribution_rel line_analytic on (line_analytic.line_id = l.id)
                    WHERE %s
                    --GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.debit_currency, l.credit_currency, l.ref, l.name, m.id, m.name, c.rounding, cc.rounding, cc.position, c.position, c.symbol, cc.symbol, p.name
                    ORDER BY %s
                ''') % (WHERE_CURRENT, ORDER_BY_CURRENT)
            else:
                sql = ('''
                                   SELECT
                                       l.id AS lid,
                                       l.date AS ldate,
                                       j.code AS lcode,
                                       p.name AS partner_name,
                                       m.name AS move_name,
                                       l.name AS lname,
                                       l.currency_id as lcurrency,
                                       COALESCE(l.debit,0) AS debit,
                                       COALESCE(l.credit,0) AS credit,
                                       COALESCE(l.debit - l.credit,0) AS balance,
                                       COALESCE(l.amount_currency,0) AS amount_currency
                                   FROM account_move_line l
                                   JOIN account_move m ON (l.move_id=m.id)
                                   JOIN account_account a ON (l.account_id=a.id)
                                   --LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                                   LEFT JOIN res_currency c ON (l.currency_id=c.id)
                                   LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                                   LEFT JOIN res_partner p ON (l.partner_id=p.id)
                                   JOIN account_journal j ON (l.journal_id=j.id)
                                   LEFT JOIN move_line_analytic_distribution_rel line_analytic on (line_analytic.line_id = l.id)
                                   WHERE %s
                                   --GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.debit_currency, l.credit_currency, l.ref, l.name, m.id, m.name, c.rounding, cc.rounding, cc.position, c.position, c.symbol, cc.symbol, p.name
                                   ORDER BY %s
                               ''') % (WHERE_CURRENT, ORDER_BY_CURRENT)

            cr.execute(sql)
            current_lines = cr.dictfetchall()
            for row in current_lines:
                row['initial_bal'] = False
                row['ending_bal'] = False

                current_balance = row['balance']
                row['balance'] = opening_balance + current_balance
                opening_balance += current_balance
                row['initial_bal'] = False
                row['lcurrency'] = row['lcurrency']

                move_lines[account.code]['lines'].append(row)

            income_type_list = ['income', 'expense', 'income_other', 'expense_depreciation',
                                'expense_direct_cost']
            if data.get('initial_balance') and account.account_type not in income_type_list:
                WHERE_FULL = WHERE + " AND l.date <= '%s'" % data.get('date_to')
            else:
                WHERE_FULL = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                    'date_to')
            WHERE_FULL += " AND a.id = %s" % account.id
            if self.branch_ids:
                sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance,
                        COALESCE(SUM(CASE WHEN l.currency_id != l.company_currency_id THEN l.amount_currency ELSE 0 END)) AS balance_in_fc
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    --LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    JOIN res_branch b ON (l.branch_id=b.id)
                    LEFT JOIN move_line_analytic_distribution_rel line_analytic on (line_analytic.line_id = l.id)
                    WHERE %s
                ''') % WHERE_FULL
            else:
                sql = ('''
                                SELECT 
                                    COALESCE(SUM(l.debit),0) AS debit, 
                                    COALESCE(SUM(l.credit),0) AS credit, 
                                    COALESCE(SUM(l.debit - l.credit),0) AS balance,
                                    COALESCE(SUM(CASE WHEN l.currency_id != l.company_currency_id THEN l.amount_currency ELSE 0 END)) AS balance_in_fc
                                FROM account_move_line l
                                JOIN account_move m ON (l.move_id=m.id)
                                JOIN account_account a ON (l.account_id=a.id)
                                --LEFT JOIN account_analytic_tag_account_move_line_rel analtag ON analtag.account_move_line_id = l.id
                                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                                JOIN account_journal j ON (l.journal_id=j.id)
                                LEFT JOIN move_line_analytic_distribution_rel line_analytic on (line_analytic.line_id = l.id)
                                WHERE %s
                            ''') % WHERE_FULL
            cr.execute(sql)
            for row in cr.dictfetchall():
                if (not row['debit'] and not row['credit']) or (
                        data.get('display_accounts') == 'balance_not_zero' and currency.is_zero(
                    row['debit'] - row['credit'])) or (
                        data.get('balance_is_zero') and (row['debit'] - row['credit']) != 0):
                    move_lines.pop(account.code, None)
                else:
                    row['ending_bal'] = True
                    row['initial_bal'] = False
                    move_lines[account.code]['lines'].append(row)
                    move_lines[account.code]['debit'] = row['debit']
                    move_lines[account.code]['credit'] = row['credit']
                    move_lines[account.code]['balance'] = row['balance']
                    move_lines[account.code]['balance_in_fc'] = row['balance_in_fc']  # MK 23AUG24
                    move_lines[account.code]['account_currency_id'] = filter_currency_id  # MK 11SEP24
                    move_lines[account.code]['company_currency_id'] = currency.id
                    move_lines[account.code]['company_currency_symbol'] = symbol
                    move_lines[account.code]['company_currency_precision'] = rounding
                    move_lines[account.code]['company_currency_position'] = position
                    move_lines[account.code]['count'] = len(current_lines)
                    move_lines[account.code]['pages'] = self.get_page_list(len(current_lines))
                    move_lines[account.code]['single_page'] = True if len(current_lines) <= FETCH_RANGE else False
        return move_lines
