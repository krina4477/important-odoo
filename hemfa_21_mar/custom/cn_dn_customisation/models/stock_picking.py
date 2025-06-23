# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import _, models, fields, api
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_number = fields.Char('Delivery Number', readonly=True, copy=False)
    dn_id = fields.Many2one('dn.tracking.number', string='Delivery Number', readonly=True, copy=False)
    use_in_backorder = fields.Boolean('Use Same DN In Backorder', default=True, help='Use same delivery number in Backorder.', copy=False)
    is_return_order = fields.Boolean('Is Return Order', copy=False)
    is_sale_return_new_dn = fields.Boolean('Is Return Order', copy=False)
    is_skip_immediate = fields.Boolean(string='Skip Immediate')
    whole_dn_id = fields.Many2one('dn.tracking.number', string='Whole DN Transfer', copy=False)

    @api.onchange('location_dest_id')
    def _onchangedn_location_dest_id(self):
        if self.location_dest_id and self.dn_id:
            self.dn_id.location_dest_id = self.location_dest_id.id
        if self.stock_request_id and self.stock_request_id.location_dest_id:
            self.dn_id.location_dest_id = self.stock_request_id.location_dest_id

    def action_confirm(self):
        res = super().action_confirm()
        self.move_line_ids.qty_done = 0
        self.move_line_ids.filtered(lambda ml: not ml.qty_done or ml.qty_done == 0.00).unlink()
        return res

    def action_assign(self):
        res = super().action_assign()
        self.move_line_ids.filtered(lambda ml: not ml.qty_done or ml.qty_done == 0.00).unlink()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        pickings = super().create(vals_list)
        dn_obj = self.env['dn.tracking.number']
        for picking in pickings:
            if self._context.get('is_cn_pos_order'):
                continue
            if picking.two_step_transfer_picking_id:
                picking.move_ids_without_package.picking_id = picking.id
                picking.dn_id = picking.two_step_transfer_picking_id.dn_id
                picking.dn_id.picking_id = picking.id
                picking.move_ids_without_package.move_line_ids.picking_id = picking.id
                continue
            if picking.dn_id:
                continue
            if picking.backorder_id.is_return_order:
                picking.is_return_order = True
            if not picking.backorder_id or not picking.backorder_id.use_in_backorder or picking.is_sale_return_new_dn:
                # if picking.picking_type_id.code == 'incoming':
                delivery_number = self.env['ir.sequence'].next_by_code('delivery.note.sequence.in') or '/'
                if picking.stock_request_id and picking.stock_request_id.location_dest_id:
                    loc_dest_id = picking.stock_request_id.location_dest_id.id
                else:
                    loc_dest_id = picking.location_dest_id.id

                picking.dn_id = dn_obj.create({
                    'name': delivery_number,
                    'picking_id': picking.id,
                    'picking_code': picking.picking_type_id.code,
                    'location_dest_id': loc_dest_id
                })

                # if picking.picking_type_id.code == 'outgoing':
                #     delivery_number = self.env['ir.sequence'].next_by_code('delivery.note.sequence.out') or '/'
                #     picking.dn_id = dn_obj.create({
                #         'name': delivery_number,
                #     })

                # if picking.picking_type_id.code == 'internal':
                #     delivery_number = self.env['ir.sequence'].next_by_code('delivery.note.sequence.internal') or '/'
                #     picking.dn_id = dn_obj.create({
                #         'name': delivery_number,
                #     })

            if picking.backorder_id.use_in_backorder:
                picking.dn_id = picking.backorder_id.dn_id.id

        return pickings

    @api.model
    def _create_picking_from_pos_order_lines(self, location_dest_id, lines, picking_type, partner=False):
        self_with_context = self.with_context(is_cn_pos_order=True)
        result = super(StockPicking, self_with_context)._create_picking_from_pos_order_lines(location_dest_id, lines, picking_type, partner)
        return result

    def _prepare_two_step_transfer(self):
        res = super()._prepare_two_step_transfer()
        for picking in self:
            move_list = []
            for move in picking.move_ids_without_package:
                move_line_list = []
                for move_line in move.move_line_ids:
                    move_line_dict = {
                        'product_id': move_line.product_id.id,
                        'product_uom_id': move_line.product_id.uom_id.id,
                        'lot_id': move_line.lot_id.id,
                        'location_id': picking.transit_location_id.id,
                        'location_dest_id': picking.location_dest_id.id,
                        'from_cartoon_number': move_line.from_cartoon_number.id,
                        'sale_truck_id': move_line.sale_truck_id.id,
                        # 'qty_done': move_line.qty_done,
                        # 'cartoon_id': move_line.cartoon_id.id or False,
                        # 'lot_name': move_line.lot_name,
                    }
                    if picking.is_two_step_transfer and picking.transit_location_id.usage in ['internal', 'transit']:
                        lot_name = move_line.truck_id.name + "-" + move_line.cartoon_id.name
                        move_line_dict.update({
                            'lot_id': False,
                            'dn_lot_id': move_line.lot_id.id,
                            'lot_name': lot_name,
                        })
                    move_line_list.append((0, 0, move_line_dict))
                move_dict = {
                    'name': move.product_id.name,
                    'product_id': move.product_id.id,
                    'product_uom_qty': move.product_uom_qty,
                    'product_uom': move.product_uom.id,
                    'location_id': picking.transit_location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                    'move_line_ids': move_line_list
                }
                move_list.append((0, 0, move_dict))
            res.update({
                'is_skip_immediate': True,
                'whole_dn_id': picking.whole_dn_id.id,
                'move_ids_without_package': move_list,
                })
        return res

    def request_work_validate(self):
        res = super().request_work_validate()
        for result in res:
            for picking in self:
                move_list = []

                intermediary_location = self.env.ref('hemfa_warehouse_stock_request.stock_location_intermediary').id 

                if picking.stock_request_id.picking_type_id.code=='internal' and picking.stock_request_id.is_stock_request_type_stock and picking.location_id.id != intermediary_location:
                    intermediary_location = self.env.ref('hemfa_warehouse_stock_request.stock_location_intermediary').id 
                    stock_picking_obj = self.env['stock.picking']
                    if picking.location_id.warehouse_id.employee_ids:
                        if self.env.user.employee_id.id not in picking.location_id.warehouse_id.employee_ids.ids:
                            raise UserError(_("You're not authorized to approved this order" ))

                    for move in picking.move_ids_without_package:
                        move_line_list = []
                        for move_line in move.move_line_ids:
                            move_line_dict = {
                                'product_id': move_line.product_id.id,
                                'product_uom_id': move_line.product_id.uom_id.id,
                                'lot_id': move_line.lot_id.id,
                                'location_id': intermediary_location,
                                'location_dest_id': picking.stock_request_id.location_dest_id.id,
                                'from_cartoon_number': move_line.from_cartoon_number.id,
                                'sale_truck_id': move_line.sale_truck_id.id,
                                'qty_done': move_line.qty_done,
                                'cartoon_id': move_line.cartoon_id.id or False,
                                'lot_name': move_line.lot_name,
                            }
                            if move_line.location_dest_id.id == intermediary_location:
                                lot_name = move_line.truck_id.name + "-" + move_line.cartoon_id.name
                                move_line_dict.update({
                                    'lot_id': False,
                                    'dn_lot_id': move_line.lot_id.id,
                                    'lot_name': lot_name,
                                })
                            move_line_list.append((0, 0, move_line_dict))

                        move_dict = {
                            'company_id': move.company_id.id,
                            'name': move.description_picking,
                            'product_id': move.product_id.id,
                            'product_uom_qty': move.product_uom_qty,
                            'product_uom': move.product_uom.id,
                            'location_id':intermediary_location ,
                            'location_dest_id': picking.stock_request_id.location_dest_id.id,
                            'move_line_ids': move_line_list,
                            'description_picking': move.description_picking,
                            'picking_type_id': picking.stock_request_id.sec_picking_type_id.id,
                        }
                        move_list.append((0, 0, move_dict))
            result.update({
                'is_skip_immediate': True,
                'move_ids_without_package': move_list,
                })
        return res

    def _get_auto_fill_carton(self):
        DnCnRec = self.env['cn.tracking.number']
        if self._context.get("is_sale_auto_fill") and self.dn_id:
            if not self.dn_id.cartoon_ids:
                sequence = self.env.ref("cn_dn_customisation.sequence_generate_cn")
                sequence.number_next_actual = len(self.dn_id.cartoon_ids) + 1
                cn_number = self.env['ir.sequence'].next_by_code('generate.cn.number') or '/'
                DnCnRec = DnCnRec.create({'name': cn_number, 'truck_id': self.dn_id.id})
            else:
                DnCnRec = self.dn_id.cartoon_ids[0]
        return DnCnRec

    def action_load_cn_dn_lines(self):
        self.ensure_one()
        move_list_create = []
        StockMoveLine = self.env['stock.move.line']
        DnCnRec = self._get_auto_fill_carton()
        for mv_line in self.move_ids:
            quantity = mv_line.product_uom_qty
            StockMove = StockMoveLine.search(
                [('location_dest_id', 'child_of', mv_line.location_id.id), ('cartoon_id', '!=', False), ('truck_id', '!=', False), ('product_id', '=', mv_line.product_id.id)])
            move_lines = StockMove.filtered(lambda ml: ml.available_cartoon_qty >= 1 and ml.truck_id.operations_type_code in ['incoming', 'internal'] or ml.picking_type_id.code in ['incoming', 'internal'])
            if move_lines:
                partial_avail_move_lines = move_lines.filtered(lambda ml: ml.available_cartoon_qty - ml.auto_fill_qty_ordered >= 1)
                sum_avail_move_lines = sum(partial_avail_move_lines.mapped('available_cartoon_qty'))
                sum_pos_move_lines = sum(partial_avail_move_lines.mapped('auto_fill_qty_ordered'))
                if sum_avail_move_lines - sum_pos_move_lines >= quantity:
                    self.move_line_ids.unlink()
                    for line in partial_avail_move_lines:
                        ml_vals = {}
                        line_wise_qty = line.available_cartoon_qty - line.auto_fill_qty_ordered
                        qty = 0
                        if quantity == 0:
                            break
                        if quantity >= line_wise_qty:
                            qty = line_wise_qty
                        else:
                            qty = quantity
                        ml_vals = dict(mv_line._prepare_move_line_vals())
                        ml_vals.update({
                            'lot_id': line.lot_id.id,
                            'from_cartoon_number': line.cartoon_id.id,
                            'sale_truck_id': line.truck_id.id,
                            'qty_done': qty,
                            'location_id': mv_line.location_id.id,
                            'cartoon_id': DnCnRec.id or False
                        })
                        if mv_line.picking_code == 'internal':
                            ml_vals.update({
                                'lot_id': False,
                                'dn_lot_id': line.lot_id.id,
                            })
                        move_list_create.append(ml_vals)
                        quantity -= qty
                        line.auto_fill_qty_ordered += qty
                        StockMoveLine += line
            move_lines = self.env['stock.move.line'].create(move_list_create)
            StockMoveLine.auto_fill_qty_ordered = 0

    def action_load_products_in_cn(self):
        self.ensure_one()
        view = self.env.ref('cn_dn_customisation.product_stock_move_barcode_form')
        return {
            'name': _('Load Product In Carton'),
            'view_mode': 'form',
            'res_model': 'product.stock.move.barcode',
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'type': 'ir.actions.act_window',
            'context': {
                'default_picking_id': self.id,
                'default_dn_id': self.dn_id.id,
            },
            'target': 'new',
        }


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    is_sale_return_new_dn = fields.Boolean(string='Is sales Return With new DN')
    code = fields.Selection(related="picking_id.picking_type_id.code")

    def _prepare_picking_default_values(self):
        res = super()._prepare_picking_default_values()
        # if self.is_sale_return_new_dn:
        #     res['is_sale_return_new_dn'] = True
        #     return res
        res['dn_id'] = self.picking_id.dn_id.id
        res['is_return_order'] = True
        return res


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    dn_id = fields.Many2one('dn.tracking.number', string='Delivery Number', copy=False)
    available_qty = fields.Float(compute="_compute_available_qty", string='Available Quantity')

    @api.depends("dn_id", 'lot_id', 'location_id')
    def _compute_available_qty(self):
        for rec in self:
            location_dest_id = rec.lot_id.quant_ids.filtered(lambda pro: pro.location_id.id == rec.dn_id.location_dest_id.id)
            rec.available_qty = 0
            if rec.location_id == rec.dn_id.location_dest_id:
                rec.available_qty = sum(location_dest_id.mapped('inventory_quantity_auto_apply'))

    @api.onchange('product_id', 'scrap_qty')
    def _onchange_scrap_product_id(self):
        self.dn_id = False
        self.lot_id = False
        if self.product_id and self.scrap_qty >=1:
            return {'domain':
                {'dn_id': [('cartoon_ids.move_line_ids.product_id','in', self.product_id.ids),
                ('picking_code', 'in', ['incoming', 'internal'])]}}

    @api.onchange('dn_id')
    def _onchange_dn_id(self):
        self.lot_id = False
        if self.dn_id:
            return {'domain':
                {'lot_id':[('product_id','=', self.product_id.id),
                ('company_id', '=', self.company_id.id),
                ('product_qty', '>=', 1),
                ('id', 'in', self.dn_id.cartoon_ids.move_line_ids.lot_id.ids)]}}
