# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
import re
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_last_sequence_domain(self, relaxed=False):
        self.ensure_one()
        if not self.date or not self.journal_id:
            return "WHERE FALSE", {}
        
        where_string = "WHERE journal_id = %(journal_id)s AND name != '/'"
        param = {'journal_id': self.journal_id.id}
        reference_move_name = False

        if not relaxed:
            domain = [('journal_id', '=', self.journal_id.id), ('id', '!=', self.id or self._origin.id),
                      ('name', 'not in', ('/', '', False))]
            
            if self.journal_id.refund_sequence:
                refund_types = ('out_refund', 'in_refund')
                domain += [('move_type', 'in' if self.move_type in refund_types else 'not in', refund_types)]
            reference_move_name = self.search(domain + [('date', '<=', self.date)], order='date desc', limit=1).name
            
            if not reference_move_name:
                reference_move_name = self.search(domain, order='date asc', limit=1).name

            if self.env['ir.config_parameter'].sudo().get_param(
                    'account_sequence_per_fiscalyear_cr.seq_per_fiscalyear'):

                fiscal_year = self.env['account.fiscal.year'].search([])

                if not fiscal_year:
                    raise ValidationError(_('Please define fiscal year with date range you want to generate sequence!'))
                # if self.date.month > 3 :
                #     reference_move_name = False
                old_date = False
                for fiscal in fiscal_year:
                    if fiscal.date_from < self.date and self.date <= fiscal.date_to and \
                            self.date.year > fiscal.date_from.year and self.date.month < fiscal.date_to.month:
                        search_data = self.search(domain + [('date', '<=', fiscal.date_to),
                                                            ('date', '>=', fiscal.date_from)],
                                                  order="name asc,date desc")
                        old_date = fiscal.date_to
                        if search_data:
                            for data in search_data.filtered(lambda x: str(fiscal.date_to.year) not in x.name):
                                reference_move_name = data.name
                                old_date = data.invoice_date
                        else:
                            reference_move_name = self.with_context(from_fiscal=fiscal.date_from.year)._get_starting_sequence()

                    elif fiscal.date_from <= self.date and self.date < fiscal.date_to and self.date.year <= fiscal.date_to.year:
                        search_data = self.search(domain + [('date', '<=', fiscal.date_to),
                                                            ('date', '>=', fiscal.date_from)],
                                                             order="name asc,date desc")
                        old_date = self.date
                        if search_data:
                            for data in search_data.filtered(lambda x: str(fiscal.date_from.year) in x.name):
                                reference_move_name = data.name
                        else:
                            reference_move_name = self.with_context(from_fiscal=fiscal.date_from.year)._get_starting_sequence()

            sequence_number_reset = self._deduce_sequence_number_reset(reference_move_name)
            if self.date.month > 3:
                sequence_number_reset = 'year'

            if sequence_number_reset == 'year':
                where_string += " AND date_trunc('year', date::timestamp without time zone) = date_trunc('year', %(date)s) "
                param['date'] = old_date if old_date else self.date
                param['anti_regex'] = re.sub(r"\?P<\w+>", "?:", self._sequence_monthly_regex.split('(?P<seq>')[0]) + '$'

            elif sequence_number_reset == 'month':
                where_string += " AND date_trunc('month', date::timestamp without time zone) = date_trunc('month', %(date)s) "
                param['date'] = self.date

            else:
                param['anti_regex'] = re.sub(r"\?P<\w+>", "?:", self._sequence_yearly_regex.split('(?P<seq>')[0]) + '$'

            if param.get('anti_regex') and not self.journal_id.sequence_override_regex:
                where_string += " AND sequence_prefix !~ %(anti_regex)s "

        if self.journal_id.refund_sequence:
            if self.move_type in ('out_refund', 'in_refund'):
                where_string += " AND move_type IN ('out_refund', 'in_refund') "
            else:
                where_string += " AND move_type NOT IN ('out_refund', 'in_refund') "
        return where_string, param, [reference_move_name]

    def _get_starting_sequence(self):
        self.ensure_one()
        year = self.date.year
        if self.env['ir.config_parameter'].sudo().get_param('account_sequence_per_fiscalyear_cr.seq_per_fiscalyear') and self.env.context.get('from_fiscal', False):
            year = self.env.context.get('from_fiscal')
        if self.journal_id.type == 'sale':
            starting_sequence = "%s/%04d/00000" % (self.journal_id.code, year)
        else:
            starting_sequence = "%s/%04d/%02d/0000" % (self.journal_id.code, year, self.date.month)

        if self.journal_id.refund_sequence and self.move_type in ('out_refund', 'in_refund'):
            starting_sequence = "R" + starting_sequence

        return starting_sequence
