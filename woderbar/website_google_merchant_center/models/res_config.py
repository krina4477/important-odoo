# -*- coding: utf-8 -*-

from odoo import fields, models, api
import werkzeug.urls


class ResConfigSettings(models.TransientModel):
    """Adds the fields for options of the Google merchant center."""
    _inherit = 'res.config.settings'

    google_content_client_id = fields.Char(string='GMC: Google Client ID')
    google_content_client_secret = fields.Char(string='GMC: Google Client Secret')
    google_content_uri = fields.Char(string='Google Content Authorization URL', readonly=True)
    google_content_authorization_code = fields.Char(string='Google Content Authorization Code')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        google_content_uri = self.env['google.merchant.center.service']._get_google_token_uri('content', scope="https://www.googleapis.com/auth/content")
        ir_config = self.env['ir.config_parameter']

        res['google_content_client_id'] = ir_config.sudo().get_param('google_content_client_id')
        res['google_content_client_secret'] = ir_config.sudo().get_param('google_content_client_secret')
        res['google_content_authorization_code'] = ir_config.sudo().get_param('google_content_authorization_code')

        res['google_content_uri'] = google_content_uri
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter']
        params.set_param('google_content_client_id', (self.google_content_client_id or ''))
        params.set_param('google_content_client_secret', (self.google_content_client_secret or ''))
        params.set_param('google_content_authorization_code', (self.google_content_authorization_code or ''))

    def sync_gmc_products(self) :
        self.env['google.merchant.center.service'].sync_products_with_gmc()

    def re_sync_gmc_products(self) :
        self.env['google.merchant.center.service'].re_sync_products_with_gmc()

    def delete_products_from_gmc(self) :
        self.env['google.merchant.center.service'].delete_products_from_gmc()

    def manual_reset_gmc_data(self) :
        self.env['product.product'].search([]).reset_gmc_data()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: