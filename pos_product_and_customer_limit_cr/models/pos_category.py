# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PosCategory(models.Model):
    _inherit = "pos.category"

    @api.model
    def _load_pos_data_domain(self, data):
        config_id = self.env['pos.config'].browse(
            data['pos.config']['data'][0]['id']
        )
        if config_id.limit_categories and config_id.iface_available_categ_ids and config_id.product_load_background and config_id.limited_products_loading:
            domain = [('id', 'in', config_id._get_available_categories().ids)]
        else:
            domain = []
        return domain