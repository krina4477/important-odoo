# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import uuid

from odoo import models, fields


class HrExpenseSheet(models.Model):
    _inherit = 'hr.leave'

    access_url = fields.Char('Portal Access URL',
                             compute='_compute_access_url',
                             help='Customer Portal URL')
    access_token = fields.Char('Security Token', copy=False)

    def _compute_access_url(self):
        for leave in self:
            leave.access_url = '/my/leaves/%s' % (leave.id)
            print("\n \n leave.access_url=========",leave.access_url)

    def _portal_ensure_token(self):
        """ Get the current record access token """
        if not self.access_token:
            # we use a `write` to force the cache clearing otherwise `return self.access_token` will return False
            self.sudo().write({'access_token': str(uuid.uuid4())})
        return self.access_token

    def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        """
            Get a portal url for this model, including access_token.
            The associated route must handle the flags for them to have any effect.
            - suffix: string to append to the url, before the query string
            - report_type: report_type query string, often one of: html, pdf, text
            - download: set the download query string to true
            - query_string: additional query string
            - anchor: string to append after the anchor #
        """
        self.ensure_one()
        url = self.access_url + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self._portal_ensure_token(),
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        print("\n \n url -----------",url)
        return url

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Expense', self.name)

    def show_change_btn(self, expense_line):
        for rec in self:
            if rec.state == "draft":
                return True
            return False


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"
