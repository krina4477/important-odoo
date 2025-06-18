# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict

from odoo import fields, http, _
from odoo.osv import expression
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.account.controllers.download_docs import _get_headers, _build_zip_from_data
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

class PortalReturnProducts(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        OrderReturn = request.env['order.return']
        if 'return_products_count' in counters:
            values['return_products_count'] = OrderReturn.search_count(self._prepare_return_order_domain(partner)) \
                if OrderReturn.has_access('read') else 0

        return values

    def _prepare_return_order_domain(self, partner):
        return [
            ('partner_id', 'in', partner.ids),
        ]
    def _get_return_order_searchbar_sortings(self):
        return {
            'request_date': {'label': _('Date'), 'order': 'request_date desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }

    def _get_return_product_searchbar_filters(self):
        return {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('state', 'in', ('draft'))]},
            'confirmed': {'label': _('Confirmed'), 'domain': [('state', 'in', ('confirmed'))]},
            'done': {'label': _('Done'), 'domain': [('state', 'in', ('done'))]},
        }

    def _return_order_get_page_view_values(self, return_sudo, access_token, **kwargs):
        # custom_amount = None
        # if kwargs.get('amount'):
        #     custom_amount = float(kwargs['amount'])
        values = {
            'page_name': 'return_product',
            **return_sudo._get_return_order_portal_extra_values(),
        }
        # import pdb
        # pdb.set_trace()
        # invoice = return_sudo
        return self._get_page_view_values(invoice, access_token, values, 'my_invoices_history', False, **kwargs)

    def _prepare_my_return_products_values(self, page, date_begin, date_end, sortby, filterby, domain=None, url="/my/return_products"):
        values = self._prepare_portal_layout_values()
        ReturnOrder = request.env['order.return']
        partner = request.env.user.partner_id
        domain = expression.AND([
            self._prepare_return_order_domain(partner)
        ])

        searchbar_sortings = self._get_return_order_searchbar_sortings()
        # default sort by order
        if not sortby:
            sortby = 'request_date'

        order = searchbar_sortings[sortby]['order']

        # searchbar_filters = self._get_return_product_searchbar_filters()
        # # default filter by value
        # if not filterby:
        #     filterby = 'all'
        # domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        url_args = {'date_begin': date_begin, 'date_end': date_end}

        if len(searchbar_sortings) > 1:
            url_args['sortby'] = sortby

        pager_values = portal_pager(
            url=url,
            total=ReturnOrder.sudo().search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args=url_args,
        )
        print("domain>>>>>>>>>>>>>>>>>>>>>>>>>.11111111111111",domain, order)

        values.update({
            'date': date_begin,
            # content according to pager and archive selected
            # lambda function to get the invoices recordset when the pager will be defined in the main method of a route
            'return_product': ReturnOrder.sudo().search(domain, order=sortby, limit=self._items_per_page, offset=pager_values['offset']),
            'page_name': 'return_product',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        print("VVVVVVVVVVVVVVVVVVVVVVVVVV   VVVVVVVVVVVVVVVVVVVVVVVVVVV", values)
        return values


    @http.route(['/my/return_products', '/my/return_products/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_return_products(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        print("11111111111111111111111111111111")
        values = self._prepare_my_return_products_values(page, date_begin, date_end, sortby, filterby)
        request.session['my_return_product_history'] = values['return_product'].ids[:100]
        return request.render("cr_portal_rma.portal_my_return_orders", values)

    @http.route(['/my/return_products/<int:return_doc_id>'], type='http', auth="public", website=True)
    def portal_my_return_products_detail(self, return_doc_id, access_token=None, report_type=None, download=False, **kw):
        print("22222222222222222222222222222222222")
        try:
            return_sudo = self._document_check_access('order.return', return_doc_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # if report_type == 'pdf' and download:
        #     # Download the official attachment(s) or a Pro Forma invoice
        #     docs_data = return_sudo._get_invoice_legal_documents_all(allow_fallback=True)
        #     if len(docs_data) == 1:
        #         headers = self._get_http_headers(invoice_sudo, report_type, docs_data[0]['content'], download)
        #         return request.make_response(docs_data[0]['content'], list(headers.items()))
        #     else:
        #         filename = invoice_sudo._get_invoice_report_filename(extension='zip')
        #         zip_content = _build_zip_from_data(docs_data)
        #         headers = _get_headers(filename, 'zip', zip_content)
        #         return request.make_response(zip_content, headers)

        if report_type in ('html', 'pdf', 'text'):
            # has_generated_invoice = bool(return_sudo.invoice_pdf_report_id)
            # request.update_context(proforma_invoice=not has_generated_invoice)
            # Use the template set on the related partner if there is.
            # This is not perfect as the invoice can still have been computed with another template, but it's a slight fix/imp for stable.
            pdf_report_name = 'cr_portal_rma.action_report_rma'
            return self._show_report(model=return_sudo, report_type=report_type, report_ref=pdf_report_name,
                                     download=download)

        values = self._return_order_get_page_view_values(return_sudo, access_token, **kw)
        # values.update({'invoice': return_sudo})
        return request.render("account.portal_invoice_page", values)