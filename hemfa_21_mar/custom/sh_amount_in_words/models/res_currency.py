# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    amount_separator = fields.Char(
        "Unit/Subunit Separator Text", translate=True)
    close_financial_text = fields.Char()
    currency_unit_label = fields.Char(translate=True)
    currency_subunit_label = fields.Char(translate=True)
