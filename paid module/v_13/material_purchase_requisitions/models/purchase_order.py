# -*- coding: utf-8 -*-


from datetime import datetime, date, timedelta
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, tools, _
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisitions',
        copy=False
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Project name',
        copy=True,
    )


    @api.model
    def _default_date(self):
        res = fields.Datetime.now()+timedelta(days=3)
        return res

    Deadline = fields.Datetime(string="Deadline", default=_default_date)

    status_order = fields.Char()

    @api.constrains('Deadline')
    def _check_Deadline_date(self):
        for event in self:
            if event.Deadline <= fields.Datetime.now():
                raise ValidationError(_('Deadline date cannot be earlier than the Date of today.'))

    def deadline_purchase_order(self):
        purchase_order_ids = self.search([('state', 'not in', ['cancel', 'done'])])
        for purchase_order in purchase_order_ids:
            nb_day_of_Deadline = purchase_order.Deadline - purchase_order.create_date
            nb_day = nb_day_of_Deadline.days
            time_difference = fields.Datetime.now() - purchase_order.create_date
            number_of_days = time_difference.days
            if number_of_days < nb_day:
                purchase_order.status_order = 'info'
            elif number_of_days == nb_day:
                purchase_order.status_order = 'info'
            elif number_of_days == nb_day+1:
                purchase_order.status_order = 'warning'
            elif number_of_days > nb_day+1:
                purchase_order.status_order = 'danger'

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisitions Line',
        copy=False
    )


