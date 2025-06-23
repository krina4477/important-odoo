# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
import pprint
import logging
_logger = logging.getLogger(__name__)


class WebsiteSale(WebsiteSale):
    
    
    @http.route(['/securianpay/validate'], type='json', auth="public", website=True)
    def securionpay_return_from_checkout(self, **data):
        _logger.info("handling redirection from SIPS with data:\n%s", pprint.pformat(data))

        # Check the integrity of the notification
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'securionpay', data
        )

        # Handle the notification data
        tx_sudo._handle_notification_data('securionpay', data)
        return {'status': True}
