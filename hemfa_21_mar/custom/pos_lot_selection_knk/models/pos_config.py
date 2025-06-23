# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    default_location_src_id = fields.Many2one(
        "stock.location", related="picking_type_id.default_location_src_id"
    )
