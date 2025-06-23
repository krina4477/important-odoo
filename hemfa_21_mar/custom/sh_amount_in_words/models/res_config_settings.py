# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ShResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sh_amount_to_word_in_upper_case = fields.Boolean(
        related="company_id.sh_amount_to_word_in_upper_case", string="Upper-case amount in words", readonly=False)
