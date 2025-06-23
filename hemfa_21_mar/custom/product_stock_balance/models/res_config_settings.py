# -*- coding: utf-8 -*-

from odoo import fields, models


class res_config_settings(models.TransientModel):
    """
    The model to keep settings of stocks' aizard
    """
    _inherit = "res.config.settings"

    group_stocks_show_only_by_button = fields.Boolean(
        "Inventory levels on button request", 
        implied_group="product_stock_balance.group_stocks_show_only_by_button",
    )
    group_stocks_show_aggregation = fields.Boolean(
        "On Hand and Forecast buttons: total by all warehouses", 
        implied_group="product_stock_balance.group_stocks_no_aggregation",
    )    
    product_stock_balance_default_levels = fields.Integer(
    	"Default Levels Expanded",
    	config_parameter="product_stock_balance_default_levels",
        default=3,
    )

