# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import fields, models

class VoucherHistory(models.Model):
    _inherit = "voucher.history"

    pos_order_id = fields.Many2one('pos.order', 'Pos Order Id')
    pos_order_line_id = fields.Many2one('pos.order.line', 'Pos OrderLine Id')