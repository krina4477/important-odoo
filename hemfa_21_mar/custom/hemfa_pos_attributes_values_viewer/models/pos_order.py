# -*- coding: utf-8 -*-

from odoo import models, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def search_order_length(self, config_data):
        return super(PosOrder,self.with_context(with_attrs=True)).search_order_length(config_data)

    @api.model
    def search_order(self, config_data, page_number):
        return super(PosOrder,self.with_context(with_attrs=True)).search_order(config_data, page_number)