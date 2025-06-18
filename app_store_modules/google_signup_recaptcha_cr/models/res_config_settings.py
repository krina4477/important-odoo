# -*- coding: utf-8 -*-
# Part of Candidroot Solutions Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    """
    Extends the 'res.config.settings' model to include Amazon Connect integration settings.
    Allows configuring Google reCAPTCHA from Odoo's settings.
    """

    _inherit = 'res.config.settings'

    show_captcha = fields.Boolean('Show Captcha', help='Show Captcha on Signup Page')
    captcha_public_key = fields.Char('Captcha Public Key', help='Public key for reCAPTCHA')
    captcha_private_key = fields.Char('Captcha Private Key', help='Private key for reCAPTCHA')


    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', "show_captcha", self.show_captcha)
        IrDefault.set('res.config.settings', "captcha_public_key", self.captcha_public_key)
        IrDefault.set('res.config.settings', "captcha_private_key", self.captcha_private_key)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        show_captcha = IrDefault._get('res.config.settings', "show_captcha")
        captcha_public_key = IrDefault._get('res.config.settings', "captcha_public_key")
        captcha_private_key = IrDefault._get('res.config.settings', "captcha_private_key")
        res.update(
            show_captcha=show_captcha,
            captcha_public_key=captcha_public_key,
            captcha_private_key=captcha_private_key,
        )
        return res