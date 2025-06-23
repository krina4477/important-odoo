# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
import logging
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
from odoo.tools.translate import _
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from collections import OrderedDict

_logger = logging.getLogger(__name__)


class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'picking_count' in counters:
            values['picking_count'] = request.env['stock.picking'].sudo().search_count([('partner_id', '=', request.env.user.partner_id.id)])
        return values

    @http.route(['/my/delivery_receipt', '/my/delivery_receipt/<int:page>'], type='http', auth="user", website=True)
    def my_payment(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None,
                            groupby='none', search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        Picking = request.env['stock.picking'].sudo()
        partner_id = request.env.user.partner_id

        domain = [('partner_id', '=', partner_id.id)]

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('partner_id', '=', partner_id.id)]}}
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('date', '>', date_begin), ('date', '<=', date_end)]

        # count for pager
        payment_count = Picking.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/delivery_receipt",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=payment_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        pickings = Picking.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_picking_history'] = pickings.ids[:100]
        values.update({
            'date': date_begin,
            'pickings': pickings,
            'page_name': 'picking',
            'pager': pager,
            'default_url': '/my/delivery_receipt',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'sortby': sortby,
            'filterby': filterby,
        })
        return request.render("portal_picking_receipt_cr.portal_delivery_receipt", values)
