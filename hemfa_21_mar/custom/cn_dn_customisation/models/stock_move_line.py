# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, Command, fields, models, _
from odoo.exceptions import ValidationError, UserError
from itertools import groupby
from odoo.tools.misc import clean_context, OrderedSet, groupby
from collections import defaultdict
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    cartoon_id = fields.Many2one('cn.tracking.number', 'To Carton', copy=False)
    truck_id = fields.Many2one('dn.tracking.number', string='Delivery Number', related="move_id.picking_id.dn_id", store=True, copy=False, readonly=False)
    sale_truck_id = fields.Many2one('dn.tracking.number', string='From Delivery Number', copy=False)
    cartoon_lot_ids = fields.Many2many('stock.lot', string='Cartoon Lots', compute="compute_cartoon_lot_ids", store=True, copy=False)
    available_cartoon_qty = fields.Float(compute="_compute_available_qty", string="Available QTY in CN", copy=False)
    total_available_cartoon_qty = fields.Float(compute="_compute_available_qty", string="Available QTY in CN", copy=False, store=True)
    purchase_return_truck_id = fields.Many2one('dn.tracking.number', string='Delivery Number', copy=False)
    available_lot_qty = fields.Float(compute="_compute_available_lot_qty", string="Available QTY in CN", copy=False)
    from_cartoon_number = fields.Many2one('cn.tracking.number', 'From Carton', copy=False)
    pos_qty_ordered = fields.Float(string="POS Ordered QTY", copy=False)
    auto_fill_qty_ordered = fields.Float(string="Auto fill QTY", copy=False)
    dn_lot_id = fields.Many2one(
        'stock.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)
    sh_barcode = fields.Char(string='SH Barcode')
    report_barcode = fields.Char(string='Barcode', compute="_compute_report_barcode")
    return_pos_qty = fields.Float(string="POS Return QTY", copy=False)

    def _compute_report_barcode(self):
        for move in self:
            if move.sh_barcode:
                move.report_barcode = move.sh_barcode
            elif move.product_id.barcode_line_ids:
                move.report_barcode = move.product_id.barcode_line_ids[0].name or ''
            else:
                move.report_barcode = move.product_id.barcode or ''

    @api.depends("truck_id", 'location_id', 'lot_id')
    def _compute_available_lot_qty(self):
        for rec in self:
            # location_dest_id = rec.lot_id.quant_ids.filtered(lambda pro: pro.location_id.id == rec.sale_truck_id.location_dest_id.id and pro.location_id.id == rec.location_id.id)
            # rec.available_lot_qty = rec.from_cartoon_number.available_qty or 0
            location_dest_id = rec.lot_id.quant_ids.filtered(lambda pro: pro.location_id.id == rec.location_id.id)
            rec.available_lot_qty = sum(location_dest_id.mapped('inventory_quantity_auto_apply'))
            # rec.available_lot_qty = sum(location_dest_id.mapped('inventory_quantity_auto_apply'))

    @api.depends("truck_id", 'location_id', 'lot_id', 'pos_qty_ordered')
    def _compute_available_qty(self):
        for rec in self:
            location_dest_id = rec.lot_id.quant_ids.filtered(lambda pro: pro.location_id.id == rec.truck_id.location_dest_id.id)
            rec.available_cartoon_qty = sum(location_dest_id.mapped('inventory_quantity_auto_apply'))
            rec.total_available_cartoon_qty = sum(location_dest_id.mapped('inventory_quantity_auto_apply'))

    @api.depends('sale_truck_id')
    def compute_cartoon_lot_ids(self):
        for rec in self:
            rec.cartoon_lot_ids = rec.sale_truck_id.cartoon_ids.move_line_ids.lot_id.ids

    @api.onchange('sale_truck_id', 'purchase_return_truck_id', 'from_cartoon_number')
    def _onchange_sale_truck_id(self):
        self.lot_id = False
        self.dn_lot_id = False
        if self.picking_code in ['outgoing']:
            if self.sale_truck_id:
                return {'domain':
                    {'lot_id':[('product_id','=', self.product_id.id),
                    ('company_id', '=', self.company_id.id),
                    ('product_qty', '>', 0),
                    ('id', 'in', self.from_cartoon_number.move_line_ids.lot_id.ids)]}}
            elif self.purchase_return_truck_id:
                return {'domain':
                    {'lot_id':[('product_id','=', self.product_id.id),
                    ('company_id', '=', self.company_id.id),
                    ('product_qty', '>', 0),
                    ('id', '=', self.purchase_return_truck_id.cartoon_ids.move_line_ids.lot_id.ids)]}}
            return {'domain':{'lot_id':[('id', 'in', self.cartoon_lot_ids.ids)]}}
        elif self.picking_code in ['internal']:
            if self.sale_truck_id:
                return {'domain':
                    {'lot_id':[('product_id','=', self.product_id.id),
                    ('company_id', '=', self.company_id.id),
                    ('product_qty', '>', 0),
                    ('id', 'in', self.from_cartoon_number.move_line_ids.lot_id.ids)],
                    'dn_lot_id':[('product_id','=', self.product_id.id),
                    ('company_id', '=', self.company_id.id),
                    ('product_qty', '>', 0),
                    ('id', 'in', self.from_cartoon_number.move_line_ids.lot_id.ids)]}}
            return {'domain':{'lot_id':[('id', 'in', self.cartoon_lot_ids.ids)],
                            'dn_lot_id':[('id', 'in', self.cartoon_lot_ids.ids)]}}

    @api.onchange('cartoon_id')
    def _onchange_cartoon_id(self):
        intermediary_location = self.env.ref('hemfa_warehouse_stock_request.stock_location_intermediary').id 
        if self.cartoon_id:
            self.lot_name = self.truck_id.name + "-" + self.cartoon_id.name
        if self.picking_id.is_two_step_transfer and self.picking_id.transit_location_id.usage in ['internal', 'transit'] and self.cartoon_id:
            self.lot_name = self.truck_id.name + "-" + self.cartoon_id.name + "-Transit"
        if self.location_dest_id.id == intermediary_location and self.cartoon_id:
            self.lot_name = self.truck_id.name + "-" + self.cartoon_id.name + "-Transit"

    @api.model_create_multi
    def create(self, vals_list):
        move_lines = super(StockMoveLine, self).create(vals_list)
        for move_line in move_lines:
            if move_line.cartoon_id:
                if move_line.move_id.picking_id and move_line.move_id.picking_id.dn_id:
                    move_line.cartoon_id.truck_id = move_line.move_id.picking_id.dn_id.id
            if self._context.get("is_dn_number") and self._context.get("is_cartoon_id"):
                move_line.cartoon_id = self._context.get("is_cartoon_id")
                move_line.truck_id = self._context.get("is_dn_number")
        return move_lines

    def _set_dn_cn_qties(self, quantity):
        StockMoveLine = self.env['stock.move.line']
        StockMove = StockMoveLine.search(
            [('location_dest_id', '=', self.location_id.id), ('cartoon_id', '!=', False), ('truck_id', '!=', False), ('product_id', '=', self.product_id.id)])
        move_lines = StockMove.filtered(lambda ml: ml.available_cartoon_qty >= 1 and ml.truck_id.operations_type_code in ['incoming', 'internal'] or ml.picking_type_id.code in ['incoming', 'internal'])
        if move_lines:
            avail_move_lines = move_lines.filtered(lambda ml: ml.available_cartoon_qty - ml.pos_qty_ordered >= quantity)
            if avail_move_lines:
                pos_move_id = avail_move_lines and avail_move_lines[0] or False
                pos_move_id.pos_qty_ordered += quantity
                self.write({
                    'lot_id': pos_move_id.lot_id.id,
                    'from_cartoon_number': pos_move_id.cartoon_id.id,
                    'sale_truck_id': pos_move_id.truck_id.id,
                })
                pos_move_id.pos_qty_ordered += quantity
                StockMoveLine += pos_move_id
            else:
                partial_avail_move_lines = move_lines.filtered(lambda ml: ml.available_cartoon_qty - ml.pos_qty_ordered >= 1)
                sum_avail_move_lines = sum(partial_avail_move_lines.mapped('available_cartoon_qty'))
                sum_pos_move_lines = sum(partial_avail_move_lines.mapped('pos_qty_ordered'))
                if sum_avail_move_lines - sum_pos_move_lines >= quantity:
                    self.qty_done = 0
                    move_list_create = []
                    for line in partial_avail_move_lines:
                        ml_vals = {}
                        line_wise_qty = line.available_cartoon_qty - line.pos_qty_ordered
                        qty = 0
                        if quantity == 0:
                            break
                        if quantity >= line_wise_qty:
                            qty = line_wise_qty
                        else:
                            qty = quantity
                        ml_vals = dict(self.move_id._prepare_move_line_vals())
                        ml_vals.update({
                            'lot_id': line.lot_id.id,
                            'from_cartoon_number': line.cartoon_id.id,
                            'sale_truck_id': line.truck_id.id,
                            'qty_done': qty,
                            'location_id': self.location_id.id or move.location_id.id,
                            'owner_id': self.owner_id.id or False,
                        })
                        move_list_create.append(ml_vals)
                        quantity -= qty
                        line.pos_qty_ordered += qty
                        StockMoveLine += line
                    self.unlink()
                    move_lines = self.env['stock.move.line'].create(move_list_create)
        # else:
            # raise ValidationError(_("Sorry, DN/CN not cointain enough quanitty for this product."))
        return StockMoveLine

    def _action_done(self):
        """ This method is called during a move's `action_done`. It'll actually move a quant from
        the source location to the destination location, and unreserve if needed in the source
        location.

        This method is intended to be called on all the move lines of a move. This method is not
        intended to be called when editing a `done` move (that's what the override of `write` here
        is done.
        """
        Quant = self.env['stock.quant']

        # First, we loop over all the move lines to do a preliminary check: `qty_done` should not
        # be negative and, according to the presence of a picking type or a linked inventory
        # adjustment, enforce some rules on the `lot_id` field. If `qty_done` is null, we unlink
        # the line. It is mandatory in order to free the reservation and correctly apply
        # `action_done` on the next move lines.
        ml_ids_tracked_without_lot = OrderedSet()
        ml_ids_to_delete = OrderedSet()
        ml_ids_to_create_lot = OrderedSet()
        for ml in self:
            # Check here if `ml.qty_done` respects the rounding of `ml.product_uom_id`.
            uom_qty = float_round(ml.qty_done, precision_rounding=ml.product_uom_id.rounding, rounding_method='HALF-UP')
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            qty_done = float_round(ml.qty_done, precision_digits=precision_digits, rounding_method='HALF-UP')
            if float_compare(uom_qty, qty_done, precision_digits=precision_digits) != 0:
                raise UserError(_('The quantity done for the product "%s" doesn\'t respect the rounding precision '
                                  'defined on the unit of measure "%s". Please change the quantity done or the '
                                  'rounding precision of your unit of measure.') % (ml.product_id.display_name, ml.product_uom_id.name))

            qty_done_float_compared = float_compare(ml.qty_done, 0, precision_rounding=ml.product_uom_id.rounding)
            if qty_done_float_compared > 0:
                if ml.product_id.tracking != 'none':
                    picking_type_id = ml.move_id.picking_type_id
                    if picking_type_id:
                        if picking_type_id.use_create_lots:
                            # If a picking type is linked, we may have to create a production lot on
                            # the fly before assigning it to the move line if the user checked both
                            # `use_create_lots` and `use_existing_lots`.
                            if ml.lot_name and not ml.lot_id:
                                lot = self.env['stock.lot'].search([
                                    ('company_id', '=', ml.company_id.id),
                                    ('product_id', '=', ml.product_id.id),
                                    ('name', '=', ml.lot_name),
                                ], limit=1)
                                if lot:
                                    ml.lot_id = lot.id
                                else:
                                    ml_ids_to_create_lot.add(ml.id)
                        elif not picking_type_id.use_create_lots and not picking_type_id.use_existing_lots:
                            # If the user disabled both `use_create_lots` and `use_existing_lots`
                            # checkboxes on the picking type, he's allowed to enter tracked
                            # products without a `lot_id`.
                            continue
                    elif ml.is_inventory:
                        # If an inventory adjustment is linked, the user is allowed to enter
                        # tracked products without a `lot_id`.
                        continue

                    if not ml.lot_id and ml.id not in ml_ids_to_create_lot:
                        ml_ids_tracked_without_lot.add(ml.id)
            elif qty_done_float_compared < 0:
                raise UserError(_('No negative quantities allowed'))
            elif not ml.is_inventory:
                ml_ids_to_delete.add(ml.id)

        if ml_ids_tracked_without_lot:
            mls_tracked_without_lot = self.env['stock.move.line'].browse(ml_ids_tracked_without_lot)
            raise UserError(_('You need to supply a Lot/Serial Number for product: \n - ') +
                              '\n - '.join(mls_tracked_without_lot.mapped('product_id.display_name')))
        ml_to_create_lot = self.env['stock.move.line'].browse(ml_ids_to_create_lot)
        ml_to_create_lot.with_context(bypass_reservation_update=True)._create_and_assign_production_lot()

        mls_to_delete = self.env['stock.move.line'].browse(ml_ids_to_delete)
        mls_to_delete.unlink()

        mls_todo = (self - mls_to_delete)
        mls_todo._check_company()

        # Now, we can actually move the quant.
        ml_ids_to_ignore = OrderedSet()
        for ml in mls_todo:
            if ml.product_id.type == 'product':
                rounding = ml.product_uom_id.rounding

                # if this move line is force assigned, unreserve elsewhere if needed
                if not ml.move_id._should_bypass_reservation(ml.location_id) and float_compare(ml.qty_done, ml.reserved_uom_qty, precision_rounding=rounding) > 0:
                    qty_done_product_uom = ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id, rounding_method='HALF-UP')
                    extra_qty = qty_done_product_uom - ml.reserved_qty
                    ml._free_reservation(ml.product_id, ml.location_id, extra_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, ml_ids_to_ignore=ml_ids_to_ignore)
                # unreserve what's been reserved
                if not ml.move_id._should_bypass_reservation(ml.location_id) and ml.product_id.type == 'product' and ml.reserved_qty:
                    Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.reserved_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)

                # move what's been actually done
                quantity = ml.product_uom_id._compute_quantity(ml.qty_done, ml.move_id.product_id.uom_id, rounding_method='HALF-UP')
                if ml.picking_code == 'internal' and ml.dn_lot_id:
                    available_qty, in_date = Quant._update_available_quantity(ml.product_id, ml.location_id, -quantity, lot_id=ml.dn_lot_id, package_id=ml.package_id, owner_id=ml.owner_id)
                else:
                    available_qty, in_date = Quant._update_available_quantity(ml.product_id, ml.location_id, -quantity, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id)
                if available_qty < 0 and ml.lot_id:
                    # see if we can compensate the negative quants with some untracked quants
                    untracked_qty = Quant._get_available_quantity(ml.product_id, ml.location_id, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    if untracked_qty:
                        taken_from_untracked_qty = min(untracked_qty, abs(quantity))
                        Quant._update_available_quantity(ml.product_id, ml.location_id, -taken_from_untracked_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id)
                        Quant._update_available_quantity(ml.product_id, ml.location_id, taken_from_untracked_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id)
                Quant.with_context(branch=ml.branch_id.id, dn_truck_id=ml.truck_id.id or False, dn_cartoon_id=ml.cartoon_id.id or False)._update_available_quantity(ml.product_id, ml.location_dest_id, quantity, lot_id=ml.lot_id, package_id=ml.result_package_id, owner_id=ml.owner_id, in_date=in_date)
            ml_ids_to_ignore.add(ml.id)
        # Reset the reserved quantity as we just moved it to the destination location.
        mls_todo.with_context(bypass_reservation_update=True).write({
            'reserved_uom_qty': 0.00,
            'date': fields.Datetime.now(),
        })


class StockMove(models.Model):
    _inherit = 'stock.move'

    truck_id = fields.Many2one('dn.tracking.number', string='Delivery Number', related="picking_id.dn_id", store=True, copy=False)
    generate_cn = fields.Integer(string='Generate CN', copy=False)
    is_return_order = fields.Boolean(related="picking_id.is_return_order")
    purchase_dn_ids = fields.Many2many('dn.tracking.number', string='Purchase Delivery Numbers', compute="_compute_purchase_dn_ids", copy=False)
    to_set_cartoon_id = fields.Many2one('cn.tracking.number', 'To Carton', copy=False)
    product_barcode = fields.Char(string='Barcode Name', compute="_compute_barcode_name", store=True, readonly=False)

    @api.depends("product_id")
    def _compute_barcode_name(self):
        for move in self:
            if move.product_id.barcode_line_ids:
                move.product_barcode = move.product_id.barcode_line_ids[0].name or ''
            else:
                move.product_barcode = move.product_id.barcode or ''

    def _compute_purchase_dn_ids(self):
        for rec in self:
            rec.purchase_dn_ids = rec.purchase_line_id.order_id.picking_ids.dn_id

    def action_generate_cn(self):
        if self.generate_cn > 0 and self.truck_id:
            sequence = self.env.ref("cn_dn_customisation.sequence_generate_cn")
            sequence.number_next_actual = len(self.truck_id.cartoon_ids) + 1
            cn_list = []
            for i in range(self.generate_cn):
                cn_number = self.env['ir.sequence'].next_by_code('generate.cn.number') or '/'
                cn_list.append({
                    'name': cn_number,
                    'truck_id': self.truck_id.id,
                })
            self.env['cn.tracking.number'].create(cn_list)
        return self.action_show_details()

    # def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
    #     res = super()._prepare_move_line_vals(quantity, reserved_quant)
    #     if self._context.get('is_cn_pos_order'):
    #         StockMove = self.env['stock.move.line'].search(
    #             [('location_dest_id', '=', res.get('location_id')), ('picking_type_id.code', 'in', ['incoming', 'internal']), ('cartoon_id', '!=', False), ('truck_id', '!=', False), ('total_available_cartoon_qty', '>=', 1), ('product_id', '=', self.product_id.id)])
    #         if StockMove:
    #             pos_move_id = StockMove and StockMove[0] or False
    #             pos_move_id.pos_qty_ordered += 1
    #             res.update({
    #                 'lot_id': pos_move_id.lot_id.id,
    #                 'from_cartoon_number': pos_move_id.cartoon_id.id,
    #                 'sale_truck_id': pos_move_id.truck_id.id,
    #             })
    #     return res

    def _add_mls_related_to_order(self, related_order_lines, are_qties_done=True):
        lines_data = self._prepare_lines_data_dict(related_order_lines)
        qty_fname = 'qty_done' if are_qties_done else 'reserved_uom_qty'
        # Moves with product_id not in related_order_lines. This can happend e.g. when product_id has a phantom-type bom.
        moves_to_assign = self.filtered(lambda m: m.product_id.id not in lines_data or m.product_id.tracking == 'none'
                                                  or (not m.picking_type_id.use_existing_lots and not m.picking_type_id.use_create_lots))
        moves_to_assign._complete_done_qties(set_quantity_done_on_move=True)
        moves_remaining = self - moves_to_assign
        existing_lots = moves_remaining._create_production_lots_for_pos_order(related_order_lines)
        move_lines_to_create = []
        mls_qties = []
        StockMoveLine = self.env['stock.move.line']
        if are_qties_done:
            for move in moves_remaining:
                for line in lines_data[move.product_id.id]['order_lines']:
                    sum_of_lots = 0
                    for lot in line.pack_lot_ids.filtered(lambda l: l.lot_name):
                        if line.product_id.tracking == 'serial':
                            qty = 1
                        else:
                            qty = abs(line.qty)
                        ml_vals = dict(move._prepare_move_line_vals())
                        if existing_lots:
                            existing_lot = existing_lots.filtered_domain([('product_id', '=', line.product_id.id), ('name', '=', lot.lot_name)])
                            quant = self.env['stock.quant']
                            if existing_lot:
                                quant = self.env['stock.quant'].search(
                                    [('lot_id', '=', existing_lot.id), ('quantity', '>', '0.0'), ('location_id', 'child_of', move.location_id.id)],
                                    order='id desc',
                                    limit=1
                                )
                            ml_vals.update({
                                'lot_id': existing_lot.id,
                                'location_id': quant.location_id.id or move.location_id.id,
                                'owner_id': quant.owner_id.id or False,
                            })
                            # if self._context.get('is_cn_pos_order'):
                            #     StockMove = self.env['stock.move.line'].search(
                            #         [('location_dest_id', '=', quant.location_id.id or move.location_id.id), ('picking_type_id.code', 'in', ['incoming', 'internal']), ('cartoon_id', '!=', False), ('truck_id', '!=', False), ('total_available_cartoon_qty', '>=', 1), ('product_id', '=', move.product_id.id)])
                            #     if StockMove:
                            #         pos_move_id = StockMove and StockMove[0] or False
                            #         pos_move_id.pos_qty_ordered += 1
                            #         ml_vals.update({
                            #             'lot_id': pos_move_id.lot_id.id,
                            #             'from_cartoon_number': pos_move_id.cartoon_id.id,
                            #             'sale_truck_id': pos_move_id.truck_id.id,
                            #         })
                        else:
                            ml_vals.update({'lot_name': lot.lot_name})
                        move_lines_to_create.append(ml_vals)
                        mls_qties.append(qty)
                        sum_of_lots += qty
                    if abs(line.qty) != sum_of_lots:
                        difference_qty = abs(line.qty) - sum_of_lots
                        ml_vals = move._prepare_move_line_vals()
                        if line.product_id.tracking == 'serial':
                            move_lines_to_create.extend([ml_vals for i in range(int(difference_qty))])
                            mls_qties.extend([1]*int(difference_qty))
                        else:
                            move_lines_to_create.append(ml_vals)
                            mls_qties.append(difference_qty)
            move_lines = self.env['stock.move.line'].create(move_lines_to_create)
            if related_order_lines.order_id.is_return_order and related_order_lines.order_id.old_pos_reference and related_order_lines.order_id.return_pos_order_id:
                ml_list = []
                for move_line, qty in zip(move_lines, mls_qties):
                    order_qty = qty
                    MoveRef = related_order_lines.order_id.return_pos_order_id.picking_ids.move_ids.filtered(lambda mv: mv.product_id == move_line.product_id)
                    for dn_ml in MoveRef.move_line_ids:
                        to_qty = 0
                        if not order_qty or order_qty <= 0.00:
                            break
                        if dn_ml.qty_done - dn_ml.return_pos_qty >= order_qty:
                            to_qty = order_qty
                        elif dn_ml.qty_done - dn_ml.return_pos_qty >= 0:
                            to_qty = dn_ml.qty_done - dn_ml.return_pos_qty
                        else:
                            to_qty = dn_ml.qty_done
                        dn_ml.return_pos_qty += to_qty
                        ml_list.append({
                            'lot_id': dn_ml.lot_id.id,
                            'cartoon_id': dn_ml.from_cartoon_number.id,
                            'truck_id': dn_ml.sale_truck_id.id,
                            'qty_done': to_qty,
                            'location_id': move_line.location_id.id or move.location_id.id,
                            'location_dest_id': move_line.location_dest_id.id or move.location_dest_id.id,
                            'owner_id': move_line.owner_id.id or False,
                            'move_id': move_line.move_id.id,
                            'product_id': move_line.product_id.id,
                            'product_uom_id': move_line.product_uom_id.id,
                            'picking_id': move_line.move_id.picking_id.id,
                        })
                        order_qty -= to_qty
                move_lines.unlink()
                self.env['stock.move.line'].create(ml_list)
            else:
                for move_line, qty in zip(move_lines, mls_qties):
                    move_line.write({qty_fname: qty})
                    StockMoveLine += move_line._set_dn_cn_qties(quantity=qty)
        else:
            for move in moves_remaining:
                for line in lines_data[move.product_id.id]['order_lines']:
                    for lot in line.pack_lot_ids.filtered(lambda l: l.lot_name):
                        if line.product_id.tracking == 'serial':
                            qty = 1
                        else:
                            qty = abs(line.qty)
                        if existing_lots:
                            existing_lot = existing_lots.filtered_domain([('product_id', '=', line.product_id.id), ('name', '=', lot.lot_name)])
                            if existing_lot:
                                available_quantity = move._get_available_quantity(move.location_id, lot_id=existing_lot, strict=True)
                                if not float_is_zero(available_quantity, precision_rounding=line.product_id.uom_id.rounding):
                                    move._update_reserved_quantity(qty, min(qty, available_quantity), move.location_id, existing_lot)
                                    continue
        StockMoveLine.pos_qty_ordered = 0

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
                'default_to_cartoon_id': self.to_set_cartoon_id.id,
                'default_move_id': self.id,
            },
            'target': 'new',
        }
