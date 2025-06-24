# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class x_radio(models.Model):
    _name = 'x_radio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'x_name'
    _description = "Radio"

    x_name = fields.Char(translate=True)
    x_studio_beschreibung = fields.Html(translate=True, string="Beschreibung")
