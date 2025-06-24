# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import werkzeug

from odoo import SUPERUSER_ID
from odoo import http
from odoo import tools , fields
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale

PPG = 20 # Products Per Page
PPR = 4  # Products Per Row

import os

def get_region():
        
        region = False
        region_obj = request.env['res.country']
        #region = region_obj.search([('name', '=', 'United States')])
        region = region_obj.search([('code', '=', 'US')])
        region_id = request.session.get('website_region')
        if region_id:
            if isinstance(region_id, (int)):
                region_id=[region_id]
            region_brw = request.env['res.country'].browse(region_id[0])
            request.session['website_sale_current_pl'] = region_brw.pricelist_id.id
            return region_brw
        else:
            region = region_obj.search([('code', '=', 'US')])
            request.session['website_region'] = region.id
            # region_brw = request.env['res.country'].browse(region.id)
            request.session['website_sale_current_pl'] = region.pricelist_id.id if region else False
            return region

class website_region(WebsiteSale):

    def get_region(self):
        return get_region()

    def get_attribute_value_ids(self, product):
        product = product.with_context(quantity=1)
        visible_attrs_ids = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id').ids
        to_currency = request.website.get_current_pricelist().currency_id
        attribute_value_ids = []
        
        for variant in product.product_variant_ids:
            if to_currency != product.currency_id:
                price = variant.currency_id.compute(variant.website_public_price, to_currency)
            else:
                price = variant.website_public_price
            visible_attribute_ids = [v.id for v in variant.attribute_value_ids if v.attribute_id.id in visible_attrs_ids]
            attribute_value_ids.append([variant.id, visible_attribute_ids, variant.website_price, price])
            
        return attribute_value_ids

    @http.route(['/shop/change_region/<model("res.country"):region_id>'], type='http', auth="public", website=True)
    def region_change(self, region_id, **post):
        if request.session['website_region']:
            if request.website.is_region_available(region_id.id):
                request.session['website_region'] = region_id.id
                region_brw = request.env['res.country'].browse(region_id.id)
                request.session['website_sale_current_pl'] = region_brw.pricelist_id.id
                request.website.sale_get_order(force_pricelist=region_brw.pricelist_id.id)
                return request.redirect(request.httprequest.referrer or '/shop')

        else:
            if request.website.is_region_available(region_id.id):
                request.session['website_region'] = region_id.id
                region_brw = request.env['res.country'].browse(region_id.id)
                request.session['website_sale_current_pl'] = region_brw.pricelist_id.id
                request.website.sale_get_order(force_pricelist=region_brw.pricelist_id.id)


            return request.redirect(request.httprequest.referrer or '/shop')

    # @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    # def product(self, product, category='', search='', **kwargs):
    #     res = super(website_region, self).product(product, category='', search='', **kwargs)
    #     return res

    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        uid=SUPERUSER_ID
        if not request.env.context.get('region'):
            region = get_region()
        else:
            region = request.env['res.country'].browse(request._context['region']).id
        
        order = request.website.sale_get_order()
        if order:
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
        else:
            compute_currency = lambda price: price

        values = {
            'website_sale_order': order,
            'compute_currency': compute_currency,
            'date': fields.Date.today(),
            'suggested_products': [],
        }
        if order:
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        if post.get('type') == 'popover':
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})

        if post.get('code_not_available'):
            values['code_not_available'] = post.get('code_not_available')

        return request.render("website_sale.cart", values)


