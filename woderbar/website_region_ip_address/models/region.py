# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo.addons.website.models.website import slugify

from geoip import geolite2
import geoip2.database
import os
from socket import gethostname, gethostbyname

from odoo import api, models, fields, tools, _ ,SUPERUSER_ID
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

class website_region(models.Model):
    _name = "website.region"
    _description = "When region has been selected that particular pricelist has been applied on webshop, and once order has been placed this price-list linked to webshop"

    name = fields.Char('Region Name', required=True)


class ResCountry(models.Model):
    _inherit = "res.country"
    _description = "When region has been selected that particular pricelist has been applied on webshop, and once order has been placed this price-list linked to webshop"

    @api.model
    def _get_language(self):
        langs = self.env['res.lang'].search([])
        return [(lang.code, lang.name) for lang in langs]
        
        
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist", required=False)
    company_id = fields.Many2one('res.company', string="Company", required=False)
    region_id = fields.Many2one('website.region',  string='Region',required=False)
    lang = fields.Selection('_get_language', string='Language')
            
                
class SaleOrder(models.Model):
    _inherit = "sale.order"

    region_country_id = fields.Many2one('res.country', string='Region/Country', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="region for current sales order.")
    company_id = fields.Many2one('res.company', 'Company', required=False, index=True, default=lambda self: self.env.company)

    

class website(models.Model):
    _inherit = 'website'

    def is_region_available(self, r_id):
        uid=SUPERUSER_ID
        """ Return a boolean to specify if a specific pricelist can be manually set on the website.
        Warning: It check only if pricelist is in the 'selectable' pricelists or the current pricelist.

        :param int pl_id: The pricelist id to check

        :returns: Boolean, True if valid / available
        """
        return r_id in [ppl.id for ppl in self.get_region_available()]

    def get_region_available(self, show_visible=False):
        uid=SUPERUSER_ID

        region_ids=self.env['res.country'].search([])
        website = request.website
        if not request.website:
            if self.env.context.get('website_id'):
                website = self.browse(self.env.context['website_id'])
            else:
                website = self.search([], limit=1)
        isocountry = request.session.geoip and request.session.geoip.get('country_code') or False
        partner = self.env.user.partner_id
        order_pl = partner.last_website_so_id and partner.last_website_so_id.state == 'draft' and partner.last_website_so_id.pricelist_id
        partner_pl = partner.property_product_pricelist
        pricelists = website._get_pl_partner_order(isocountry, show_visible,
                                                   website.user_id.sudo().partner_id.property_product_pricelist.id,
                                                   request.session.get('website_sale_current_pl'),
                                                   website.pricelist_ids,
                                                   partner_pl=partner_pl and partner_pl.id or None,
                                                   order_pl=order_pl and order_pl.id or None)
        
        return region_ids


    def get_current_region(self):
        ir_param = self.env['ir.config_parameter'].sudo()
        goipsetup = ir_param.get_param('website_region_ip_address.goip_setup')

        SUPERUSER_ID = 1       
        region = False
        region_obj = self.env['res.country']
        region_id = request.session.get('website_region')

        ip_add  = os.popen("wget http://ipecho.net/plain -O - -q ; echo").read()        
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        ip_db = path + '/' + 'GeoLite2-Country.mmdb'
        reader = geoip2.database.Reader(ip_db)
        
        if ip_add and len(ip_add) > 1:
            match = reader.country(ip_add[:-1])
            if match:
                locate_country = match.country.iso_code

        if goipsetup == 'allow':
            region_brw = region_id
        else:
            region_brw = self.env['res.country'].search([('code','=',locate_country)]).id

        if region_brw:
            request.session['website_region'] = region_id
        else:
            region = region_obj.search([('code', '=', 'US')])
            region_list = []
            region_list.append(region.id)
            region_brw = region_list
            
        regin_data = self.env['res.country'].browse(region_brw) 
        
        request.session['website_sale_current_pl'] = regin_data.pricelist_id.id
        request.session['website_region'] = regin_data.id      
        return regin_data



    def get_region_category(self):
        uid=SUPERUSER_ID
        list_of_region = []
        region_ids=self.env['res.country'].search([])
        
        for region_id in region_ids:
            region_data = region_id
            if region_data.region_id.id not in list_of_region:
                list_of_region.append(region_data.region_id.id)
            
            self.env.uid = 1    
            regions_ids=self.env['website.region'].search([('id','in',list_of_region)])
            regions_data = regions_ids
        return regions_data

    def get_region_child_category(self,country_id):
        country_ids=self.env['res.country'].search([('region_id', '=', country_id)])
        return country_ids

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    goip_setup = fields.Selection([
        ('disallow','Do not allow to change country after GEOIP setup'),
        ('allow','Allow to change country after GEOIP setup.'),
    ], default='disallow')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        ir_conf_param = self.env['ir.config_parameter']
        ir_conf_param.set_param('website_region_ip_address.goip_setup', self.goip_setup)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_param = self.env['ir.config_parameter'].sudo()
        goipsetup = ir_param.get_param('website_region_ip_address.goip_setup')
        res.update(
            goip_setup = goipsetup
        )
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
