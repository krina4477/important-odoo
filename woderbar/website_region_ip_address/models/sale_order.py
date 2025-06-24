# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import random
import odoo

from odoo import SUPERUSER_ID, tools
from odoo.tools.translate import _
from odoo.addons.website_sale.models.website import Website

# from geoip import geolite2
# import geoip2.database
import os
from socket import gethostname, gethostbyname

from odoo import api, models, fields, tools, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

class Website(models.Model):
    _inherit = 'website'



    def sale_get_order(self, force_create=False, force_region=None,code=None, update_pricelist=False,update_region = False, force_pricelist=False):
        """ Return the current sale order after mofications specified by params.
        :param bool force_create: Create sale order if not already existing
        :param str code: Code to force a pricelist (promo code)
                         If empty, it's a special case to reset the pricelist with the first available else the default.
        :param bool update_pricelist: Force to recompute all the lines from sale order to adapt the price with the current pricelist.
        :param int force_pricelist: pricelist_id - if set,  we change the pricelist with this one
        :returns: browse record for the current sale order
        """
        self.ensure_one()
        partner = self.env.user.partner_id
        sale_order_id = request.session.get('sale_order_id')
        if not sale_order_id and not self.env.user._is_public():
            last_order = partner.last_website_so_id
            if last_order:
                available_pricelists = self.get_pricelist_available()
                # Do not reload the cart of this user last visit if the cart uses a pricelist no longer available.
                sale_order_id = last_order.pricelist_id in available_pricelists and last_order.id

        # Test validity of the sale_order_id
        sale_order = self.env['sale.order'].sudo().browse(sale_order_id).exists() if sale_order_id else None

        if not (sale_order or force_create or code):
            if request.session.get('sale_order_id'):
                request.session['sale_order_id'] = None
            return self.env['sale.order']

        if self.env['product.pricelist'].browse(force_pricelist).exists():
            pricelist_id = force_pricelist
            request.session['website_sale_current_pl'] = pricelist_id
            update_pricelist = True
        else:
            pricelist_id = request.session.get('website_sale_current_pl') or self.get_current_pricelist().id

        if not self._context.get('pricelist'):
            self = self.with_context(pricelist=pricelist_id)

        region_id = request.session.get('website_region')
        # create so if needed
        if not sale_order:
            # TODO cache partner_id session
            affiliate_id = request.session.get('affiliate_id')
            if self.env['res.users'].sudo().browse(affiliate_id).exists():
                salesperson_id = affiliate_id
            else:
                salesperson_id = request.website.salesperson_id.id
            addr = partner.address_get(['delivery', 'invoice'])
            region_id = request.session.get('website_region')
            region_brw = self.env['res.country'].browse(region_id)
            company_id = region_brw.company_id
            region_id = region_brw.region_id
            sale_order = self.env['sale.order'].sudo().create({
                'partner_id': partner.id,
                'pricelist_id': pricelist_id,
                'payment_term_id': self.sale_get_payment_term(partner),
                'team_id': self.salesteam_id.id,
                'partner_invoice_id': addr['invoice'],
                'partner_shipping_id': addr['delivery'],
                'user_id': salesperson_id or self.salesperson_id.id,
                'region_country_id':region_id.id,
                # 'company_id':company_id.id,
            })
            if company_id:
                sale_order.company_id = company_id
            # set fiscal position
            if request.website.partner_id.id != partner.id:
                sale_order.onchange_partner_shipping_id()
            else: # For public user, fiscal position based on geolocation
                country_code = request.session['geoip'].get('country_code')
                if country_code:
                    country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1).id
                    fp_id = request.env['account.fiscal.position'].sudo()._get_fpos_by_region(country_id)
                    sale_order.fiscal_position_id = fp_id
                else:
                    # if no geolocation, use the public user fp
                    sale_order.onchange_partner_shipping_id()

            request.session['sale_order_id'] = sale_order.id

            if request.website.partner_id.id != partner.id:
                partner.write({'last_website_so_id': sale_order_id})

        # case when user emptied the cart
        if not request.session.get('sale_order_id'):
            request.session['sale_order_id'] = sale_order.id

        # check for change of pricelist with a coupon
        pricelist_id = pricelist_id or partner.property_product_pricelist.id

        # check for change of partner_id ie after signup
        if sale_order.partner_id.id != partner.id and request.website.partner_id.id != partner.id:
            flag_pricelist = False
            if pricelist_id != sale_order.pricelist_id.id:
                flag_pricelist = True
            fiscal_position = sale_order.fiscal_position_id.id

            # change the partner, and trigger the onchange
            sale_order.write({'partner_id': partner.id})
            sale_order.onchange_partner_id()
            sale_order.write({'partner_invoice_id': partner.id})
            sale_order.onchange_partner_shipping_id() # fiscal position
            sale_order['payment_term_id'] = self.sale_get_payment_term(partner)

            # check the pricelist : update it if the pricelist is not the 'forced' one
            values = {}
            if sale_order.pricelist_id:
                if sale_order.pricelist_id.id != pricelist_id:
                    values['pricelist_id'] = pricelist_id
                    update_pricelist = True

            # if fiscal position, update the order lines taxes
            if sale_order.fiscal_position_id:
                sale_order._compute_tax_id()

            # if values, then make the SO update
            if values:
                sale_order.write(values)

            # check if the fiscal position has changed with the partner_id update
            recent_fiscal_position = sale_order.fiscal_position_id.id
            if flag_pricelist or recent_fiscal_position != fiscal_position:
                update_pricelist = True

        if code and code != sale_order.pricelist_id.code:
            code_pricelist = self.env['product.pricelist'].search([('code', '=', code)], limit=1)
            if code_pricelist:
                pricelist_id = code_pricelist.id
                update_pricelist = True
        elif code is not None and sale_order.pricelist_id.code:
            # code is not None when user removes code and click on "Apply"
            pricelist_id = partner.property_product_pricelist.id
            update_pricelist = True


        # update the pricelist
        if update_pricelist:
            request.session['website_sale_current_pl'] = pricelist_id
            region_id = request.session.get('website_region')
            region_brw = self.env['res.country'].browse(region_id)
            company_id = region_brw.company_id
            values = {'pricelist_id': pricelist_id,'region_country_id': region_id,'company_id':company_id.id}
            sale_order.write(values)
            for line in sale_order.order_line:
                if line.exists():
                    sale_order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)
                    
                    
        

        return sale_order


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Use in view attrs. Need to required state_id if Country is India.
    l10n_in_country_code = fields.Char(related="country_id.code", string="Country code")

    @api.constrains('vat', 'country_id')
    def l10n_in_check_vat(self):
        # for partner in self.filtered(lambda p: p.commercial_partner_id.country_id.code == 'IN' and p.vat and len(p.vat) != 15):
        #     raise UserError(_('The GSTIN [%s] for partner [%s] should be 15 characters only.') % (partner.vat, partner.name))

        try:
            for partner in self.filtered(lambda p: p.commercial_partner_id.country_id.code == 'IN' and p.vat and len(p.vat) == 15):
                raise UserError(_('The GSTIN [%s] for partner [%s] should be 15 characters only.') % (partner.vat, partner.name))
        except Exception as e:
            # raise UserError(_('The GSTIN [%s] for partner [%s] should be 15 characters only.') % (partner.vat, partner.name))
            raise e