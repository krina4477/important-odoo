# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request

class cart_website_sale(http.Controller):
    @http.route(['/shop/clear_cart'], type='http', auth="user", website=True)
    def clear_cart(self):
        order = request.website.sale_get_order()
        if order:
            order.website_order_line.unlink()
        return request.redirect('/shop/cart')
