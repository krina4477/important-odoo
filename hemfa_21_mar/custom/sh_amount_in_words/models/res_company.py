# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ShResCompany(models.Model):
    _inherit = "res.company"

    sh_amount_to_word_in_upper_case = fields.Boolean(
        "Upper-case amount in words")
