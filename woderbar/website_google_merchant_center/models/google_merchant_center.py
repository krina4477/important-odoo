# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning

import time
import json
import requests
from werkzeug import urls

import logging
_logger = logging.getLogger(__name__)

TIMEOUT = 20

GOOGLE_AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_API_BASE_URL = 'https://www.googleapis.com'

unique_id_increment = 0
def get_unique_id():
    """Generates a unique ID.

    The ID is based on the current UNIX timestamp and a runtime increment.

    Returns:
      A unique string.
    """
    global unique_id_increment
    if unique_id_increment is None:
        unique_id_increment = 0
    unique_id_increment += 1
    return "%d%d" % (int(time.time()), unique_id_increment)

class GoogleMerchantCenterService(models.Model):
    _name = 'google.merchant.center.service'
    _description = "GMC Service"

    #ACS: Copy from google account but used access_token only instead of refresh token
    #Becuse of return UIR had to add this method
    @api.model
    def _get_google_token_uri(self, service, scope):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        web_base_url = get_param("web.base.url")
        encoded_params = urls.url_encode({
            'scope': scope,
            'redirect_uri': web_base_url + '/google_content/authentication',
            'client_id': get_param('google_%s_client_id' % service),
            'response_type': 'code',
        })
        return '%s?%s' % (GOOGLE_AUTH_ENDPOINT, encoded_params)

    #ACS: Copy from google account but used access_token only instead of refresh token
    #Becuse of return UIR had to add this method
    @api.model
    def generate_refresh_token(self, service, authorization_code):
        """ Call Google API to refresh the token, with the given authorization code
            :param service : the name of the google service to actualize
            :param authorization_code : the code to exchange against the new refresh token
            :returns the new refresh token
        """
        Parameters = self.env['ir.config_parameter'].sudo()
        client_id = Parameters.get_param('google_%s_client_id' % service)
        client_secret = Parameters.get_param('google_%s_client_secret' % service)
        redirect_uri = Parameters.get_param('google_redirect_uri')

        web_base_url = Parameters.get_param("web.base.url")
        redirect_uri = web_base_url + '/google_content/authentication'

        # Get the Refresh Token From Google And store it in ir.config_parameter
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        data = {
            'code': authorization_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': "authorization_code"
        }
        try:
            req = requests.post(GOOGLE_TOKEN_ENDPOINT, data=data, headers=headers, timeout=TIMEOUT)
            req.raise_for_status()
            content = req.json()
        except IOError:
            error_msg = _("Something went wrong during your token generation. Maybe your Authorization Code is invalid or already expired")
            raise self.env['res.config.settings'].get_config_warning(error_msg)
        return content.get('access_token')

    #ACS: Copy from google account
    @api.model
    def get_access_token(self, scope=None):
        Config = self.env['ir.config_parameter'].sudo()
        google_content_refresh_token = Config.get_param('google_content_refresh_token')
        user_is_admin = self.env.is_admin()
        if not google_content_refresh_token:
            raise UserError(_("Google Shopping API is not yet configured. Please contact your administrator."))
        google_content_client_id = Config.get_param('google_content_client_id')
        google_content_client_secret = Config.get_param('google_content_client_secret')
        #For Getting New Access Token With help of old Refresh Token
        data = {
            'client_id': google_content_client_id,
            'refresh_token': google_content_refresh_token,
            'client_secret': google_content_client_secret,
            'grant_type': "refresh_token",
            'scope': scope or 'https://www.googleapis.com/auth/content'
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        try:
            req = requests.post(GOOGLE_TOKEN_ENDPOINT, data=data, headers=headers, timeout=TIMEOUT)
            req.raise_for_status()
        except requests.HTTPError:
            if user_is_admin:
                dummy, action_id = self.env['ir.model.data'].get_object_reference('base_setup', 'action_general_configuration')
                msg = _("Something went wrong during the token generation. Please request again an authorization code .")
                raise RedirectWarning(msg, action_id, _('Go to the configuration panel'))
            else:
                raise UserError(_("Google Shopping API is not yet configured. Please contact your administrator."))
        return req.json().get('access_token')

    def sync_product_with_gmc(self, products):
        """ Update products on Google merchant center
            Param: Products: browse list of records for product.product
        """
        def get_names(cat):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res

        currency = self.env.user.company_id.currency_id.name
        count = 1
        for product in products:
            #Display ads id
            if product.google_display_ads_id:
                displayAdsId = product.google_display_ads_id
            else:
                displayAdsId = 'ADS%s' % get_unique_id()
                product.write({'google_display_ads_id': displayAdsId})
            product_data = {
                'displayAdsId': displayAdsId,
                'title': product.name,
                'description': product.description_sale,
                #Use product template url as variants are not shown sepratly.
                'link': product.google_merchant_center_id.website + "/shop/product/%s" % (product.product_tmpl_id.id,),
                'imageLink': product.google_merchant_center_id.website + '/web/image/%s/%s/%s/image.jpg' % ('product.template', product.product_tmpl_id.id, 'image_1024'),
                #Note: Instead of passing website url passsed backend URl because Store not accept image without type
                'contentLanguage': product.google_content_language,
                'targetCountry': product.google_target_country,
                'channel': product.google_channel,
                'availability': product.google_availability,
                'condition': product.google_condition,
                'googleProductCategory': " > ".join(reversed(get_names(product.google_product_category_id))),
                'productTypes': [" > ".join(reversed(get_names(product.categ_id)))],
                'brand': product.google_product_brand_id and product.google_product_brand_id.name or '',
                'price': {
                    'value': product.gmc_list_price,
                    'currency': currency},
                'shipping': [{
                    'country': product.google_target_country,
                    'service': product.google_shipping,
                    'price': {'value': product.google_shipping_amount,
                              'currency': currency}
                }],
                'shippingWeight': {
                   'value': product.weight * 1000, 
                   'unit': 'grams'
                },
            }

            if product.google_mcid:
                product_data.pop('targetCountry')
                product_data.pop('contentLanguage')
                product_data.pop('channel')
            else:
                offerId = 'CM%s' % get_unique_id()
                product_data.update({'offerId': offerId, 'id': offerId})

            #Check if identifierExists than only add mpn
            if product.google_identifier_exists:
                if not product.google_barcode_as_gtin and product.google_gtin:
                    product_data.update({'gtin': product.google_gtin})
                elif product.google_barcode_as_gtin and product.barcode:
                    product_data.update({'gtin': product.barcode})
                if product.google_default_code_as_mpn:
                    product_data.update({'mpn': product.default_code})
            else:
                product_data.update({'identifier_exists': 'no'})

            #add some optional attributes
            if product.google_gender:
                product_data.update({'gender': product.google_gender})
            if product.google_age_group:
                product_data.update({'ageGroup': product.google_age_group})
            if product.google_product_size_id:
                product_data.update({'sizes': [product.google_product_size_id and product.google_product_size_id.name or '']})
            if product.google_product_color_id:
                product_data.update({'color': product.google_product_color_id and product.google_product_color_id.name or '',})
            if product.google_expiration_date:
                #pass date in perticular formate
                expiration_date = product.google_expiration_date.strftime('%Y-%m-%d')
                product_data.update({'expirationDate': expiration_date})

            #Optionla Attributes for Remarketing
            if product.google_display_ads_similar_ids:
                product_data.update({'displayAdsSimilarIds': [prod.google_display_ads_id for prod in product.google_display_ads_similar_ids]})
            if product.google_display_ads_title:
                product_data.update({'displayAdsTitle': product.google_display_ads_title})
            if product.google_display_ads_link:
                product_data.update({'displayAdsLink': product.google_display_ads_link})
            if product.google_display_ads_value:
                product_data.update({'displayAdsValue': product.google_display_ads_value})
            if product.google_excluded_destination:
                product_data.update({'destinations': {
                   'destinationName': 'DisplayAds', 
                   'intention': 'excluded'}
                })

            token = self.get_access_token()
            jason_data_set = json.dumps(product_data)
            if product.google_mcid:
                mc_product_id = product.google_channel + ':' + product.google_content_language + ':' + product.google_target_country+ ':' + product.google_mcid
                url = "https://shoppingcontent.googleapis.com/content/v2.1/%s/products/%s" % (product.google_merchant_center_id.name, mc_product_id)
                reqreply = requests.patch(url, jason_data_set, headers={'accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % (token)})
            else:
                url = "https://shoppingcontent.googleapis.com/content/v2.1/%s/products" % product.google_merchant_center_id.name
                reqreply = requests.post(url, jason_data_set, headers={'accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % (token)})

            reqreply_text = json.loads(reqreply.text)
            if reqreply.status_code!=200:
                product.gmc_lisitng_response = json.loads(reqreply.text)

            if reqreply.status_code==200:
                if product.google_mcid:
                    product.write({'google_sync_date': fields.Date.today()})
                else:
                    product.write({'google_mcid': offerId, 'google_sync_date': fields.Date.today()})

    def sync_products_with_gmc(self) :
        """Sync New products which is still not synced on center"""
        products = self.env['product.product'].search([('sync_with_mc','=',True), ('website_published','=',True), ('google_product_brand_id','!=',False), ('google_merchant_center_id','!=',False),('google_mcid','=',False)])
        _logger.info('Total products to be synced------ %s', len(products))
        self.sync_product_with_gmc(products)

    def re_sync_products_with_gmc(self) :
        """Re Sync all products"""
        products = self.env['product.product'].search([('sync_with_mc','=',True), ('google_mcid','!=',False)], order='google_sync_date asc')
        _logger.info('Total products to be synced------ %s', len(products))
        self.sync_product_with_gmc(products)

    def delete_product_from_gmc(self, products):
        """ Delete products on Google merchant center
            Param: Products: browse list of records for product.product
        """
        for product in products:
            if product.google_mcid:
                mc_product_id = product.google_channel + ':' + product.google_content_language + ':' + product.google_target_country+ ':' + product.google_mcid
                token = self.get_access_token()
                _logger.info('Product-------  %s',product)
                url = "https://shoppingcontent.googleapis.com/content/v2.1/%s/products/%s" % (product.google_merchant_center_id.name, mc_product_id)
                reqreply = requests.delete(url, headers={'accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % (token)})
                if reqreply.status_code==200:
                    product.google_mcid = ''
                    self.env.cr.commit()
                if reqreply.status_code!=200:
                    try:
                        product.gmc_lisitng_response = json.loads(reqreply.text)
                    except:
                        pass

    def delete_products_from_gmc(self) :
        """Delete all products"""
        products = self.env['product.product'].search([('sync_with_mc','=',True), ('google_mcid','!=',False)])
        self.delete_product_from_gmc(products)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: