# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from datetime import datetime, timedelta


class SaleMarginReport(models.TransientModel):
    _name = 'sale.margin.wizard'
    _description = 'Sale Margin Report'

    start_date = fields.Date(string="From Date", required=True)
    end_date = fields.Date(string="To Date", required=True)
    customers = fields.Many2many('res.partner', string="Customers")
    products = fields.Many2many('product.template', string="Products")
    sales_person = fields.Many2many('res.users', string="Sales Persons")
    highlight_negative = fields.Boolean(string="Highlight Negative Margin records")
    margin_nature = fields.Selection([('all', "All"), ('positive', "Positive Margin"), ('negative', "Negative Margin")],
                                     string="Product Margin Nature", required=True)

    @api.onchange('margin_nature')
    def onchange_margin_nature(self):
        if self.margin_nature == 'positive' or self.margin_nature == 'negative':
            self.highlight_negative = False

    def print_margin_xcel(self):
        pass

    def print_margin_report(self):
        records = []
        products = []
        sales_persons = []
        customers = []

        for product in self.products:
            products.append(product.id)
        for customer in self.customers:
            customers.append(customer.id)
        for sales_person in self.sales_person:
            sales_persons.append(sales_person.id)

        if self.products:

            if self.customers:

                if self.sales_person:
                    margin_recs = self.env['sale.order.line'].search(
                        [('order_id.date_order', '>', self.start_date), ('order_id.date_order', '<', self.end_date),
                         ('product_id.id', 'in', products), ('order_id.partner_id.id', 'in', customers),
                         ('order_id.user_id.id', 'in', sales_persons)])
                else:
                    margin_recs = self.env['sale.order.line'].search(
                        [('order_id.date_order', '>', self.start_date), ('order_id.date_order', '<', self.end_date),
                         ('product_id.id', 'in', products), ('order_id.partner_id.id', 'in', customers)])
            else:
                if self.sales_person:
                    margin_recs = self.env['sale.order.line'].search(
                        [('order_id.date_order', '>', self.start_date), ('order_id.date_order', '<', self.end_date),
                         ('product_id.id', 'in', products), ('order_id.user_id.id', 'in', sales_persons)])
                else:
                    if self.margin_nature == 'positive':
                        margin_recs = self.env['sale.order.line'].search(
                            [('order_id.date_order', '>', self.start_date), ('order_id.date_order', '<', self.end_date),
                             ('product_id.id', 'in', products)])
        else:
            if self.customers:
                if self.sales_person:
                    margin_recs = self.env['sale.order.line'].search(
                        [('order_id.date_order', '>', self.start_date), ('order_id.date_order', '<', self.end_date),
                         ('order_id.partner_id.id', 'in', customers),
                         ('order_id.user_id.id', 'in', sales_persons)])
                else:
                    margin_recs = self.env['sale.order.line'].search(
                        [('order_id.date_order', '>', self.start_date), ('order_id.date_order', '<', self.end_date),
                         ('order_id.partner_id.id', 'in', customers)])
            else:
                if self.sales_person:
                    margin_recs = self.env['sale.order.line'].search(
                        [('order_id.date_order', '>', self.start_date), ('order_id.date_order', '<', self.end_date),
                         ('order_id.user_id.id', 'in', sales_persons)])
                else:
                    margin_recs = self.env['sale.order.line'].search(
                        [('order_id.date_order', '>', self.start_date), ('order_id.date_order', '<', self.end_date)])
        for rec in margin_recs:
            vals = {
                'sale_order': rec.order_id.name,
                'date': rec.order_id.date_order.date(),
                'product_name': rec.product_id.name,
                'customer': rec.order_id.partner_id.name,
                'sales_person': rec.order_id.user_id.name,
                'quantity': rec.product_uom_qty,
                'unit_price': rec.product_id.lst_price,
                'cost': rec.cost,
                'sub_total': rec.price_subtotal,
                'margin_amount': rec.margin,
                'margin_percentage': rec.margin_percentage
            }
            records.append(vals)

        data = {
            'reports': self.read()[0],
            'records': records,
        }
        return self.env.ref("sales_margin.action_report_salemargin").report_action(self, data=data)
