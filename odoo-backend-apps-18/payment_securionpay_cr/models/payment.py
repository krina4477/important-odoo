# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import json
import hmac
import base64
import hashlib
import logging
from odoo import api, fields, models, _
from odoo.addons.payment import utils as payment_utils
from werkzeug import urls
from odoo.exceptions import ValidationError
from odoo.http import request
import requests
from werkzeug.urls import url_join
from requests.auth import HTTPBasicAuth
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

_logger = logging.getLogger(__name__)

SUPPORTED_CURRENCIES = ('ARS', 'BRL', 'CLP', 'COP', 'MXN', 'PEN', 'USD')

class PaymentAcquirerSecurionpay(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('securionpay', 'Securionpay')], ondelete={'securionpay': 'cascade'})
    securionpay_secret_key = fields.Char(required_if_provider='securionpay', groups='base.group_user')
    securionpay_publishable_key = fields.Char(required_if_provider='securionpay', string="Public Key", groups='base.group_user')


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'securionpay':
            return res

        partner_obj = self.env['res.partner']
        currency_obj = self.env['res.currency']

        base_url = self.get_base_url()
        data = {
            'company': self.company_id.name,
            'email': partner_obj.browse(processing_values.get('partner_id')).email,
            'name': partner_obj.browse(processing_values.get('partner_id')).name,
            'description': request.website.sale_get_order().name,
            'amount': request.website.sale_get_order().amount_total,
            'so_id': request.website.sale_get_order().id,
            'key': self.provider_id.securionpay_publishable_key,
            'image': base_url + "/logo.png",
            'provider_id': self.provider_id.id,
            'returndata': '/shop/payment/validate'
        }

        amount_charge = {
            "charge": {
                "amount": '{:0>10}'.format(str(processing_values.get('amount')).split('.')[0]) + '{:0<2}'.format(
                    str(processing_values.get('amount')).split('.')[1]),
                "currency": currency_obj.browse(processing_values.get('currency_id')).name
            },
        }
        hash_value = json.dumps(amount_charge, sort_keys=True, separators=(',', ':'))
        digest = hmac.new(self.provider_id.securionpay_secret_key.encode(), msg=hash_value.encode(),
                          digestmod=hashlib.sha256).hexdigest()
        hash_value = base64.b64encode((digest + '|' + hash_value).encode()).decode()
        data['checkout_request'] = hash_value

        processing_values.update(data)

        return dict(processing_values)

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'securionpay' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')
        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'securionpay')])
        if not tx:
            raise ValidationError(
                "Securionpay: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _securionpay_form_validate(self, data):
        if data.get('charge', 'id') and data['charge']['id']:
            self.write({
                'state': 'done',
                'provider_reference': data['charge']['id'],
            })
            if self.partner_id and not self.token_id:
                if data.get('customer', 'id') and data['customer']['id']:
                    card_url = "https://api.securionpay.com/customers/"+data['customer']['id']
                    resp = requests.get(card_url, data={'limit': 3}, auth=HTTPBasicAuth(str(self.provider_id.securionpay_secret_key), ''))
                    content = json.loads(resp.content)
                    token_id = self.env['payment.token'].create({
                        'payment_details': content['cards'][0]['last4'],
                        'provider_ref':  data['customer']['id'],
                        'provider_id': self.provider_id.id,
                        'partner_id': self.partner_id.id,
                        'card_ref': content['defaultCardId'],
                        'verified':True,
                    })
                    self.token_id = token_id
                    if self.state == 'done':
                        self.last_state_change = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            return True
        else:
            error = _('Securionpay: feedback error')
            _logger.info(error)
            self.write({
                'state': 'error',
                'state_message': data['error']
            })
            return False

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'securionpay':
            return
        if self.tokenize:
            self._securionpay_form_validate(notification_data)
        self.provider_reference = notification_data['charge']['id']
        self._set_done()
        self._cron_post_process()
    
        
class PaymentTokenSecurionpay(models.Model):
    _inherit = 'payment.token'

    card_ref = fields.Char("Card Ref.")
