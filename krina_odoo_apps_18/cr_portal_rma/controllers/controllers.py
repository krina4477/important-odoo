from odoo import http, _
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_sale.controllers import main
from odoo.http import request, route
from odoo import api, fields, models

class WebsiteSale(main.WebsiteSale):

    @route(['/portal/order/return_lines'], type='json', auth="public", website=True)
    def order_return_lines(self, order_id,picking_id):
        order = request.env['sale.order'].sudo().browse(int(order_id))
        picking = request.env['stock.picking'].sudo().browse(int(picking_id))
        picking_sale_ids = picking.move_ids_without_package.mapped('sale_line_id').ids
        lines = []
        for line in order.order_line.filtered(lambda l: l.qty_delivered > 0 and l.id in picking_sale_ids):
            returnline = request.env['order.return.line'].sudo().search([('line_id', '=', line.id)])
            returnline_done = returnline.filtered(lambda s: s.state == 'done')
            print("returnline_done>>>>>>>",returnline_done)
            related_move = line.sudo().move_ids.filtered(lambda m: m.picking_id.id == int(picking_id))
            total_return_qty = sum(returnline.mapped('qty')) if returnline else 0
            total_return_qty_done = sum(returnline_done.mapped('qty')) if returnline_done else 0
            lines.append({
                'line_id': line.id,
                'product_name': line.product_id.display_name,
                'qty_delivered': (line.qty_delivered + total_return_qty_done) - total_return_qty,
            })

        return {'lines': lines}

    @route(['/portal/return_order/order_create'], type='json', auth="public", website=True)
    def return_order_create(self, order_id, picking_id, lines):
        # {'line_75': 1}

        order = request.env['sale.order'].sudo().browse([int(order_id)])
        print("/portal/return_order/order_create>>>>>>>>>>>>>>>>>>>>>>>>>>.",picking_id)
        picking_id = request.env['stock.picking'].sudo().browse(int(picking_id))
        print("picking_id>>>>>>11111>>>.",picking_id)
        return_doc = request.env['order.return'].sudo().search([('website_order_id', '=', int(order_id)),('state', '=', 'draft'),('picking_id', '=', (int(picking_id)))])
        print("return_doc>>>>>>2222>>>.", return_doc)
        data = {}
        lines_list = []
        if order and lines:
            for key, value in lines.items():
                line_id = int(key.split('_')[1])
                line = request.env['sale.order.line'].sudo().browse(int(line_id))
                returnline = request.env['order.return.line'].sudo().search([('line_id', '=', line.id),('state', '=', 'draft'),('return_order_id.picking_id', '=', (int(picking_id)))])
                if line:
                    related_move = line.sudo().move_ids.filtered(lambda m: m.picking_id.id == picking_id.id)
                    if returnline:
                        returnline.sudo().write({'qty': returnline.qty + int(value)})
                    else:
                        lines_list.append((0, 0, {
                            'name': line.name,
                            'product_id': line.product_id.id,
                            'qty': int(value),
                            'price_unit': line.price_unit,
                            'uom_id': line.product_uom.id,
                            'line_id': line.id,
                            'move_id': related_move.id,
                            'tax_id': [(6,0, line.tax_id.ids)]
                        }))
            print("ddddddddddddddddddsssssssssss",return_doc)
            if not return_doc:
                request.env['order.return'].sudo().create({
                    # 'name': line.order_id.name,
                    'partner_id': picking_id.partner_id.id,
                    'request_date': fields.datetime.now(),
                    'website_order_id': line.order_id.id,
                    'order_return_lines': lines_list,
                    'state': 'draft',
                    'picking_id': int(picking_id),
                    'company_id': line.order_id.company_id.id,
                    'currency_id': line.order_id.currency_id.id,

                })



        # lines = []
        # for line in order.order_line.filtered(lambda l: l.qty_delivered > 0):
        #     lines.append({
        #         'line_id': line.id,
        #         'product_name': line.product_id.display_name,
        #         'qty_delivered': line.qty_delivered,
        #     })
        return True