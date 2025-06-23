# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, http, _
from odoo.http import request

class WeatherController(http.Controller):

    @http.route('/weather_info/', type='json', auth='user')
    def weather_info(self, model, fields, domain):
        result = request.env[model].sudo().search_read(domain, fields)
        return result
