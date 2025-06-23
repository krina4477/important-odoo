# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import base64
from collections import OrderedDict
from datetime import datetime, timedelta

from odoo import fields, http, _
from odoo.addons.portal.controllers import portal
# from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class CustomerPortal(portal.CustomerPortal):
    _items_per_page = 20

    @http.route(['/new_leave', ], type='http', auth="user", website=True)
    def new_leave_route(self, **kwargs):
        """
        This route pass the backend data and render the form in frontend
        """
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', (request.env.user).id)])
        manager_id = employee_id.parent_id
        # holiday_status_ids = request.env['hr.leave.type'].sudo().search(
        #     ['|', ('requires_allocation', '=', 'no'),
        #      '&', ('has_valid_allocation', '=', True),
        #      '&', ('max_leaves', '>', 0),
        #      '|', ('allows_negative', '=', True),
        #      '&', ('virtual_remaining_leaves', '>', 0),
        #      ('allows_negative', '=', False)])

        employee_leave_allocation = request.env['hr.leave.allocation'].sudo().search(
            [('employee_id', '=', employee_id.id)])
        holiday_status_ids = employee_leave_allocation.mapped('holiday_status_id')
        return request.render("hr_leave_portal_cr.new_leave_web_page", {'employee_id': employee_id,
                                                                        'manager_id': manager_id or False,
                                                                        'holiday_status_ids': holiday_status_ids})

    @http.route(['/leave/apply'], type='http', auth="user", website=True)
    def leave_apply(self, **post):
        """
        This route create record in 'hr.leave' and data fetch from frontend
        """
        leave_data = {}
        if post.get('request_unit_half') == '1':
            leave_data.update({
                'holiday_status_id': int(post.get('holiday_status_id')),
                'employee_id': int(post.get('employee_id')),
                'manager_id': int(post.get('manager_id')),
                'request_unit_half': True,
                'request_date_from_period': post.get('request_date_from_period'),
                'request_date_from': datetime.strptime(post.get('date_from'), '%Y-%m-%d'),
                'request_date_to': datetime.strptime(post.get('date_from'), '%Y-%m-%d'),
                'name': post.get('name'),
                'state': 'confirm',
                'number_of_days': 0.5,
            })

        elif post.get('request_unit_hours') == '1':
            leave_data.update({
                'holiday_status_id': int(post.get('holiday_status_id')),
                'employee_id': int(post.get('employee_id')),
                'manager_id': int(post.get('manager_id')),
                'request_unit_hours': True,
                'request_hour_from': post.get('request_from'),
                'request_hour_to': post.get('request_to'),
                'request_date_from': datetime.strptime(post.get('date_from'), '%Y-%m-%d'),
                'request_date_to': datetime.strptime(post.get('date_from'), '%Y-%m-%d'),
                'name': post.get('name'),
                'state': 'confirm',
            })

        elif (not post.get('request_unit_half') == '1' and not post.get('request_unit_hours') == '1'):
            leave_data.update({
                'holiday_status_id': int(post.get('holiday_status_id')),
                'employee_id': int(post.get('employee_id')),
                'manager_id': int(post.get('manager_id')),
                'request_date_from': datetime.strptime(post.get('date_from'), '%Y-%m-%d'),
                'request_date_to': datetime.strptime(post.get('date_to'), '%Y-%m-%d'),
                'name': post.get('name'),
                'state': 'confirm',
            })

        attachment = request.httprequest.files.get('attachment')
        if attachment:
            attachment_data = {
                'name': attachment.filename,
                'datas': base64.b64encode(attachment.read()),
                'res_model': 'hr.leave',
                'type': 'binary'
            }
            attachment_id = request.env['ir.attachment'].sudo().create(attachment_data)
        leave = request.env['hr.leave'].sudo().create(leave_data)
        if attachment:
            attachment_id.sudo().write({'res_id': leave.id})
        return request.redirect('/my/leaves/%s' % (leave.id))

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        user = request.env.user
        HrLeave = request.env['hr.leave'].sudo()
        if 'leave_count' in counters:
            if HrLeave.search_count([('employee_id.user_id', '=', user.id)]) > 1:
                values['leave_count'] = HrLeave.search_count([('employee_id.user_id', '=', user.id)])
            else:
                values['leave_count'] = 1
        return values

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_leave_custom(self, page=1, date_begin=None, sortby=None, filterby='all', search=None,
                               groupby='none', search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        user_id = request.env.user
        leave_list = request.env['hr.leave']
        domain = [('employee_id.user_id', '=', user_id.id)]
        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name desc'},
        }
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('employee_id.user_id', '=', user_id.id)]}}

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        # count for pager
        leave_count = leave_list.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/leaves",
            url_args=kw,
            total=leave_count,
            page=page,
            step=20,
        )
        leave_total = leave_list.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        leave_allocations = request.env['hr.leave.allocation'].sudo().search(
            [('state', '=', 'validate'), ('employee_id.user_id', '=', user_id.id)])
        request.session['my_leave_history'] = leave_total.ids[:100]
        values.update({
            'date': date_begin,
            'leave_total': leave_total,
            'leave_allocations': leave_allocations,
            'page_name': 'leaves_page',
            'pager': pager,
            'default_url': '/my/leaves',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'sortby': sortby,
            'filterby': filterby,
        })
        return request.render("hr_leave_portal_cr.portal_my_leave_template", values)

    @http.route(['/my/leaves/<int:leave_list_id>'], type='http', auth="public", website=True)
    def portal_leave_page_custom(self, leave_list_id, report_type=None, access_token=None, message=False,
                                 download=False, **kw):
        try:
            HrLeave = self._document_check_access('hr.leave', leave_list_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if HrLeave:
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_leave_%s' % HrLeave.id)
            author = HrLeave.partner_id if request.env.user._is_public() else request.env.user.partner_id
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % HrLeave.id] = now
                msg = _('Leave viewed by user %s', HrLeave.employee_id.user_id.partner_id.name)
                HrLeave.message_post(
                    author_id=author.id,
                    body=msg,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )
        values = {
            'leave_list': HrLeave,
            'message': message,
            'page_name': 'leave_list_detail',
            'token': access_token,
            'bootstrap_formatting': True,
            'partner_id': HrLeave.employee_id.user_id.partner_id.id,
            'report_type': 'html',
        }
        history = request.session.get('my_leave_history', [])
        values.update(get_records_pager(history, HrLeave))
        return request.render('hr_leave_portal_cr.leave_list_custom_portal_template', values)
