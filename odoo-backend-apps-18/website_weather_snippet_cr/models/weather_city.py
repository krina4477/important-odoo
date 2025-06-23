# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, api, models, _

class WeatherCity(models.Model):
    _name = 'weather.city'

    name = fields.Char('Name')
    zip = fields.Char('Zip')
    weather_name = fields.Char('Weather Name', compute="_compute_weather_name", store=True)
    weather_id = fields.Char('Weather ID', compute="_compute_weather_name", store=True)
    partner_latitude = fields.Float('Latitude', digits=(10, 7))
    partner_longitude = fields.Float('Longitude', digits=(10, 7))
    state_id = fields.Many2one(string="State", comodel_name='res.country.state')
    country_id = fields.Many2one(string="Country", comodel_name='res.country')
    date_localization = fields.Date(string='Geolocation Date')

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    @api.depends("name", "zip", "state_id", "country_id", 'partner_latitude', 'partner_longitude')
    def _compute_weather_name(self):
        for res in self:
            if res.name:
                res.weather_name = res.name.lower().replace(' ', '-')
                latitude = res.partner_latitude
                latitude_str = ''
                if latitude < 0:
                    latitude_str += 'n'
                latitude = format(abs(latitude), '.2f')
                latitude_str += latitude.replace('.', 'd')

                longitude = res.partner_longitude
                longitude_str = ''
                if longitude < 0:
                    longitude_str += 'n'
                longitude = format(abs(longitude), '.2f')
                longitude_str += longitude.replace('.', 'd')
                res.weather_id = latitude_str + longitude_str
            else:
                res.weather_name = ''
                res.weather_id = ''

    def city_geo_localize(self):
        geo_obj = self.env['base.geocoder']
        for rec in self:
            search = geo_obj.geo_query_address(zip=rec.zip, city=rec.name, state=rec.state_id.name, country=rec.country_id.name)
            result = geo_obj.geo_find(search, force_country=rec.country_id.name)
            if result is None:
                search = geo_obj.geo_query_address(city=rec.name, state=rec.state_id.name, country=rec.country_id.name)
                result = geo_obj.geo_find(search, force_country=rec.country_id.name)
            if result:
                rec.write({
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.Date.context_today(rec)
                })
                rec._compute_weather_name()