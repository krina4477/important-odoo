# -*- coding: utf-8 -*-
###############################################################################
from odoo import models, fields, api, _

class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    is_sales_person_visible = fields.Boolean(string="Salesperson")
    sales_person_selection = fields.Selection([('on_order_line', 'Order Line'),
                                               ('on_order', 'On Order')], string="Applied On", default='on_order')






class PosOrderLine(models.Model):
    """ The class PosOrder is used to inherit pos.order.line """

    _inherit = 'pos.order.line'
    user_id = fields.Many2one('res.users', string='Salesperson',
                              help="You can see salesperson here")



class PosOrder(models.Model):
    """ The class PosOrder is used to inherit pos.order.line """

    _inherit = 'pos.order'
    sales_user_id = fields.Many2one('res.users', string='Salesperson',
                              help="You can see salesperson here")

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['sales_user_id'] = ui_order.get('sales_user_id', False)
        return res

