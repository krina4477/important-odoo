# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import format_date


class SequenceMixin(models.AbstractModel):
    _inherit = 'sequence.mixin'

    @api.constrains(lambda self: (self._sequence_field, self._sequence_date_field))
    def _constrains_date_sequence(self):
        # Make it possible to bypass the constraint to allow edition of already messed up documents.
        # /!\ Do not use this to completely disable the constraint as it will make this mixin unreliable.
        constraint_date = fields.Date.to_date(self.env['ir.config_parameter'].sudo().get_param(
            'sequence.mixin.constraint_start_date',
            '1970-01-01'
        ))
        for record in self:
            date = fields.Date.to_date(record[record._sequence_date_field])
            sequence = record[record._sequence_field]
            if sequence and date and date > constraint_date:
                format_values = record._get_sequence_format_param(sequence)[1]
                if (
                        format_values['year'] and format_values['year'] != date.year % 10 ** len(
                    str(format_values['year']))
                        or format_values['month'] and format_values['month'] != date.month
                ):
                    
                    if format_values['year'] == date.year % 10 ** len(str(format_values['year'])):
                        if self.env['ir.config_parameter'].sudo().get_param(
                                'account_sequence_per_fiscalyear_cr.seq_per_fiscalyear'):
                            fiscal_year = self.env['account.fiscal.year'].search([])
                            flag = False
                            for fiscal in fiscal_year:
                                if fiscal.date_from < self.date and self.date <= fiscal.date_to and self.date.year > fiscal.date_from.year:
                                    flag = True
                            if not flag:
                                raise ValidationError(_(
                                    "The %(date_field)s (%(date)s) doesn't match the sequence number of the related %(model)s (%(sequence)s)\n"
                                    "You will need to clear the %(model)s's %(sequence_field)s to proceed.\n"
                                    "In doing so, you might want to resequence your entries in order to maintain a continuous date-based sequence.",
                                    date=format_date(self.env, date),
                                    sequence=sequence,
                                    date_field=record._fields[record._sequence_date_field]._description_string(
                                        self.env),
                                    sequence_field=record._fields[record._sequence_field]._description_string(self.env),
                                    model=self.env['ir.model']._get(record._name).display_name,
                                ))


    def _get_last_sequence(self, relaxed=False, with_prefix=None, lock=True):
        self.ensure_one()
        if self._sequence_field not in self._fields or not self._fields[self._sequence_field].store:
            raise ValidationError(_('%s is not a stored field', self._sequence_field))
        
        where_string, param, orig_seq = self._get_last_sequence_domain(relaxed)
        if orig_seq and self.env['ir.config_parameter'].sudo().get_param('account_sequence_per_fiscalyear_cr.seq_per_fiscalyear'):
            return (orig_seq or [None])[0]
        
        if self.id or self.id.origin:
            where_string += " AND id != %(id)s "
            param['id'] = self.id or self.id.origin

        if with_prefix is not None:
            where_string += " AND sequence_prefix = %(with_prefix)s "
            param['with_prefix'] = with_prefix

        query = f"""
                SELECT {{field}} FROM {self._table}
                {where_string}
                AND sequence_prefix = (SELECT sequence_prefix FROM {self._table} {where_string} ORDER BY id DESC LIMIT 1)
                ORDER BY sequence_number DESC
                LIMIT 1
        """
        if lock:
            query = f"""
            UPDATE {self._table} SET write_date = write_date WHERE id = (
                {query.format(field='id')}
            )
            RETURNING {self._sequence_field};
            """
        else:
            query = query.format(field=self._sequence_field)


        self.flush([self._sequence_field, 'sequence_number', 'sequence_prefix'])
        self.env.cr.execute(query, param)
        res = self.env.cr.fetchone()
        return (res or [None])[0]
