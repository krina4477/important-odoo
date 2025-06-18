# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tests.common import Form
from collections import defaultdict

class OrderReturn(models.Model):
    _name = 'order.return'
    _inherit = ['portal.mixin', 'mail.thread.main.attachment', 'mail.activity.mixin', 'sequence.mixin']
    _description = 'Return Orders'
    _sequence_date_field = 'request_date'

    name = fields.Char(
        string="Document",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))
    partner_id = fields.Many2one("res.partner", string="Customer")
    website_order_id = fields.Many2one("sale.order",string="Sale Order")

    picking_id = fields.Many2one("stock.picking",string="Picking Document")
    request_date = fields.Datetime("Return Request On", default=fields.Datetime.now)
    reason = fields.Text("Reason For Return")
    order_return_lines = fields.One2many('order.return.line', 'return_order_id', string='Order Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string="State")
    return_picking_id = fields.Many2one("stock.picking",string="Return Document")
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
    )

    sale_order_count = fields.Integer(
        "Invoice Count",
        compute='_compute_so_count',
    )
    delivery_order_count = fields.Integer(
        "Invoice Count",
        compute='_compute_delivery_count',
    )
    return_order_count = fields.Integer(
        "Invoice Count",
        compute='_compute_return_order_count',
    )

    def _compute_so_count(self):
        for rec in self:
            if rec.website_order_id:
                rec.sale_order_count = len(rec.website_order_id)
            else:
                rec.sale_order_count = 0

    def _compute_delivery_count(self):
        for rec in self:
            if rec.picking_id:
                rec.delivery_order_count = len(rec.picking_id)
            else:
                rec.delivery_order_count = 0

    def _compute_return_order_count(self):
        for rec in self:
            if rec.return_picking_id:
                rec.return_order_count = len(rec.return_picking_id)
            else:
                rec.return_order_count = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                request_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['request_date'])
                ) if 'request_date' in vals else None
                vals['name'] = self.env['ir.sequence'].with_company(vals.get('company_id')).next_by_code(
                    'order.return', sequence_date=request_date) or _("New")

        return super().create(vals_list)

    def test_confirm(self):
        # self.state = 'confirmed'
        if self.picking_id:
            print("move_ids///////////////////////", self._context)
            print("move_ids/////////self.picking_id.id//////////////", self.picking_id.id)
            data = {}
            for orl in self.order_return_lines:
                print(">>>>>>>>>>>>>.", orl.move_id)
                data[orl.move_id.id] = orl.qty
            print("data>????????????????????", data)
            # wizard = self.env['stock.return.picking'].with_context(return_mode=True,move_data=data,
            #      return_doc=self.id).create({'picking_id': self.picking_id.id})
            # wizard_form = Form(wizard).save()
            # print("wizard_form>>>>>>>>>",wizard_form)

            return_wizard = self.env['stock.return.picking'].with_context(default_picking_id=self.picking_id.id ,active_id=self.picking_id.id,
                                                                          active_ids=self.picking_id.ids,
                                                                          return_mode=True,
                                                                          move_data=data,
                                                                          return_doc=self.id).create({
            })
            print("======================================================", return_wizard)
            return_wizard._compute_moves_locations()
            res = return_wizard.action_create_returns()
            print("res???????????????????????????",res)
            # wizard_form.action_create_returns()

            # return {
            #     'type': 'ir.actions.act_window',
            #     'name': 'Return',
            #     'res_model': 'stock.return.picking',
            #     'view_mode': 'form',
            #     'target': 'new',
            #     'context': {
            #         'default_picking_id': self.picking_id.id,
            #         'return_mode': True,
            #         'move_data': data,
            #         'return_doc': self.id
            #     }
            # }

    def action_view_so(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "domain": [('id', 'in', self.website_order_id.ids)],
            "context": {"create": False, 'default_move_type': 'out_invoice'},
            "name": _("Customer Invoices"),
            'view_mode': 'list,form',
        }

    def action_view_delivery(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "domain": [('id', 'in', self.picking_id.ids)],
            "context": {"create": False, 'default_move_type': 'out_invoice'},
            "name": _("Customer Invoices"),
            'view_mode': 'list,form',
        }

    def action_view_return(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "domain": [('id', 'in', self.return_picking_id.ids)],
            "context": {"create": False, 'default_move_type': 'out_invoice'},
            "name": _("Customer Invoices"),
            'view_mode': 'list,form',
        }

    def _get_return_order_portal_extra_values(self):
        self.ensure_one()
        return {
            'return_product': self,
            'currency': self.currency_id,
        }


class OrderReturnLine(models.Model):
    _name = 'order.return.line'
    _description = 'Return Orders Lines'

    name = fields.Text("Description")
    return_order_id = fields.Many2one("order.return", string="Return Order Id", ondelete='cascade')
    product_id = fields.Many2one("product.product", string="Product", required=True)
    line_id = fields.Many2one("sale.order.line", string="Orderline Id", required=True)
    move_id = fields.Many2one("stock.move", string="Move Id")
    qty = fields.Float("Quantity")
    price_unit = fields.Float("Unit Price")
    uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string="State", related='return_order_id.state')

    company_id = fields.Many2one(
        related='return_order_id.company_id',
        store=True, index=True, precompute=True)

    currency_id = fields.Many2one(
        related='return_order_id.currency_id',
        depends=['return_order_id.currency_id'])

    tax_id = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        compute='_compute_tax_id',
        store=True, readonly=False, precompute=True,
        context={'active_test': False},
        check_company=True)

    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute='_compute_amount',
        store=True, precompute=True)

    price_tax = fields.Float(
        string="Total Tax",
        compute='_compute_amount',
        store=True, precompute=True)

    price_total = fields.Monetary(
        string="Total",
        compute='_compute_amount',
        store=True, precompute=True)

    product_type = fields.Selection(related='product_id.type', depends=['product_id'])

    def _get_custom_compute_tax_cache_key(self):
        """Hook method to be able to set/get cached taxes while computing them"""
        return tuple()

    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._prepare_base_line_for_taxes_computation(
            self,
            **{
                'tax_ids': self.tax_id,
                'quantity': self.qty,
                'partner_id': self.return_order_id.website_order_id.partner_id,
                'currency_id': self.return_order_id.website_order_id.currency_id,
                'rate': self.return_order_id.website_order_id.currency_rate,
                **kwargs,
            },
        )

    @api.depends('qty', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for line in self:
            base_line = line._prepare_base_line_for_taxes_computation()
            self.env['account.tax']._add_tax_details_in_base_line(base_line, line.company_id)
            line.price_subtotal = base_line['tax_details']['raw_total_excluded_currency']
            line.price_total = base_line['tax_details']['raw_total_included_currency']
            line.price_tax = line.price_total - line.price_subtotal

    @api.depends('product_id', 'company_id')
    def _compute_tax_id(self):
        lines_by_company = defaultdict(lambda: self.env['order.return.line'])
        cached_taxes = {}
        for line in self:
            if line.product_type == 'combo':
                line.tax_id = False
                continue
            lines_by_company[line.company_id] += line
        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = None
                if line.product_id:
                    taxes = line.product_id.taxes_id._filter_taxes_by_company(company)
                if not line.product_id or not taxes:
                    # Nothing to map
                    line.tax_id = False
                    continue
                fiscal_position = line.return_order_id.website_order_id.fiscal_position_id
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                cache_key += line._get_custom_compute_tax_cache_key()
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result
                # If company_id is set, always filter taxes by the company
                line.tax_id = result


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_status(self, picking):
        print("picking>>>>>>>>.",picking)
        full_request_sumbited = 'no'
        return_order = self.env['order.return'].sudo().search([('website_order_id', '=', self.id),('picking_id', '=', picking.id)])
        picking_sale_ids = picking.move_ids_without_package.mapped('sale_line_id').ids
        delivered_qty = sum(self.order_line.filtered(lambda sl: sl.id in picking_sale_ids).mapped('qty_delivered'))
        print("delivered_qty>>>>>>>>>>.",delivered_qty)

        total_requested = 0.0
        for rec in return_order:
            total_requested += sum(rec.order_return_lines.mapped('qty'))
        if delivered_qty == total_requested:
            full_request_sumbited = "yes"
        print("total_requested>>>>>>>>>>.", total_requested)
        print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD", full_request_sumbited)
        return full_request_sumbited

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def action_create_returns(self):
        self.ensure_one()
        new_picking = self._create_return()
        print("s>>>>>>>>>>>>>>>>>>>>PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPpp>>>>>>>>.", self._context)
        if new_picking:
            if self._context.get('return_doc', False):
                doc_id = int(self._context.get('return_doc', False))
                order_return_rec = self.env['order.return'].sudo().browse([doc_id])
                if order_return_rec:
                    order_return_rec.state = 'confirmed'
                    order_return_rec.return_picking_id = new_picking.id
        return {
            'name': _('Returned Picking'),
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'res_id': new_picking.id,
            'type': 'ir.actions.act_window',
            'context': self.env.context,
        }

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        if self and self._context and self._context.get('return_mode', False):
            move_quant_dict = self._context.get('move_data', False)
            quantity = move_quant_dict.get(stock_move.id, 0)
            if move_quant_dict:
                import pdb
                pdb.set_trace()
                return {
                    'product_id': stock_move.product_id.id,
                    'quantity': quantity,
                    'move_id': stock_move.id,
                    'uom_id': stock_move.product_id.uom_id.id,
                }
            else:
                return {
                    'product_id': stock_move.product_id.id,
                    'quantity': 0,
                    'move_id': stock_move.id,
                    'uom_id': stock_move.product_id.uom_id.id,
                }
        else:
            return {
                'product_id': stock_move.product_id.id,
                'quantity': 0,
                'move_id': stock_move.id,
                'uom_id': stock_move.product_id.uom_id.id,
            }