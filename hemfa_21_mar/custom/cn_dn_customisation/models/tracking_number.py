from odoo import api, fields, models, _
from odoo.exceptions import UserError

class DNTrackingNumber(models.Model):
    _name = "dn.tracking.number"
    _description = "Tracking Number of Delivery Number"

    name = fields.Char(string='Delivery Number', default=lambda self: _('New'))
    cartoon_ids = fields.One2many('cn.tracking.number', 'truck_id', string='Carton Numbers')
    total_cartoons = fields.Integer(string='Total Cartons', compute="_compute_total_cartoons")
    total_qty = fields.Float(string='Total Quantity', compute="_compute_total_quantity", store=True, 
        help='Total quantity containd by tracking number.')
    total_avail_qty = fields.Float(string='Total Available Quantity', compute="_compute_total_quantity")
    picking_id = fields.Many2one('stock.picking', string='Picking', readonly=True)
    picking_code = fields.Char(string='Picking Type')
    move_line_ids = fields.Many2many('stock.move.line', string='Stock Moves', compute="_compute_move_line_ids")
    location_dest_id = fields.Many2one(
        'stock.location', 'Location',
        help="Location where the system will stock the finished products.")
    cn_product_detail_ids = fields.Many2many('cn.product.details', string='Products', compute="_compute_product_detail_ids")
    generate_cn = fields.Integer(string='Generate Carton', copy=False)
    operations_type_code = fields.Selection([('internal', 'Internal'), ('incoming', 'Incoming'), ('outgoing', 'Outgoing')], string='Picking Type')

    @api.onchange('operations_type_code')
    def _onchnage_operations_type_code(self):
        if self.operations_type_code:
            self.picking_code = self.operations_type_code

    # @api.depends('picking_id')
    # def _compute_location_dest_id(self):
    #     for dn in self:
    #         dn.location_dest_id = dn.picking_id.location_dest_id

    def action_view_internal_stock_picking(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        action['domain'] = [('whole_dn_id', 'in', self.ids)]
        return action

    def action_view_stock_move_lines(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_line_action")
        product_ids = self.cartoon_ids.move_line_ids.product_id.ids
        action['domain'] = ['&', ('product_id', 'in', product_ids), '|', ('cartoon_id', 'in', self.cartoon_ids.ids), ('from_cartoon_number', 'in', self.cartoon_ids.ids)]
        return action

    @api.depends('cartoon_ids', 'cartoon_ids.move_line_ids', 'cartoon_ids.move_line_ids.qty_done', 'cartoon_ids.available_qty')
    def _compute_move_line_ids(self):
        for rec in self:
            rec.move_line_ids = rec.cartoon_ids.move_line_ids.ids

    @api.depends('cartoon_ids', 'cartoon_ids.move_line_ids', 'cartoon_ids.move_line_ids.qty_done', 'cartoon_ids.available_qty')
    def _compute_product_detail_ids(self):
        dn_cn_product_details = self.env['cn.product.details']
        for rec in self:
            cn_product_list = []
            rec.cn_product_detail_ids.unlink()
            for cn in rec.cartoon_ids.move_line_ids.product_id:
                move_line_ids = rec.cartoon_ids.move_line_ids
                available_qty = sum(move_line_ids.filtered(lambda lt: lt.product_id.id == cn.id and lt.location_dest_id == rec.location_dest_id).mapped('available_cartoon_qty'))
                done_qty = sum(move_line_ids.filtered(lambda lt: lt.product_id.id == cn.id and lt.location_dest_id == rec.location_dest_id).mapped('qty_done'))
                cn_product = {
                    'product_id': cn.id, 'available_qty': available_qty,
                    'total_qty': done_qty}
                cn_product_list.append(cn_product)
            all_pro = dn_cn_product_details.create(cn_product_list)
            self.cn_product_detail_ids = all_pro.ids

    @api.depends('cartoon_ids', 'cartoon_ids.move_line_ids', 'cartoon_ids.move_line_ids.qty_done')
    def _compute_total_quantity(self):
        for rec in self:
            kunes = rec.cartoon_ids.move_line_ids.filtered(lambda dn: dn.location_dest_id.id == rec.location_dest_id.id)
            rec.total_qty = sum(kunes.mapped('qty_done')) or 0
            rec.total_avail_qty = sum(kunes.mapped('available_cartoon_qty')) or 0

    def _compute_total_cartoons(self):
        for rec in self:
            rec.total_cartoons = len(rec.cartoon_ids)

    def unlink(self):
        for rec in self:
            if rec.cartoon_ids and any(cartoon.total_qty > 0 for cartoon in rec.cartoon_ids):
                raise UserError(_("You can not delete the Delivery Number which cartoon contains the done Quantity."))
        return super().unlink()

    def action_transfer_whole_dn(self):
        self.ensure_one()
        view = self.env.ref('cn_dn_customisation.transfer_whole_dn_form')
        return {
            'name': _('Transfer Whole DN'),
            'view_mode': 'form',
            'res_model': 'transfer.whole.dn',
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'type': 'ir.actions.act_window',
            'context': {
                'default_dn_id': self.id,
                'default_location_id': self.location_dest_id.id},
            'target': 'new',
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'delivery.note.sequence.in') or _("New")
        return super().create(vals_list)

    def action_generate_cn(self):
        if self.generate_cn > 0:
            sequence = self.env.ref("cn_dn_customisation.sequence_generate_cn")
            sequence.number_next_actual = len(self.cartoon_ids) + 1
            cn_list = []
            for i in range(self.generate_cn):
                cn_number = self.env['ir.sequence'].next_by_code('generate.cn.number') or '/'
                cn_list.append({
                    'name': cn_number,
                    'truck_id': self.id,
                })
            self.env['cn.tracking.number'].create(cn_list)
        return True


class CNTrackingNumber(models.Model):
    _name = "cn.tracking.number"
    _description = "Tracking Number of Cartoon Number"

    name = fields.Char(string='Carton Number', default=lambda self: _('New'), readonly=True)
    truck_id = fields.Many2one('dn.tracking.number',string='Truck Number', readonly=True)
    move_line_ids = fields.One2many('stock.move.line', 'cartoon_id', string='Move Lines')
    total_qty = fields.Float(string='Total Quantity', compute="_compute_total_qty", store=True)
    available_qty = fields.Float(string='Available Quantity', compute="_compute_available_qty")

    def print_cn_report(self):
        return self.env.ref('cn_dn_customisation.report_cn').report_action(self)

    @api.depends('move_line_ids', 'move_line_ids.qty_done')
    def _compute_available_qty(self):
        for rec in self:
            location_dest_id = rec.move_line_ids.lot_id.quant_ids.filtered(lambda pro: pro.location_id.id == rec.truck_id.location_dest_id.id)
            rec.available_qty = sum(location_dest_id.mapped('inventory_quantity_auto_apply'))

    @api.depends('move_line_ids', 'move_line_ids.qty_done', 'name')
    def _compute_total_qty(self):
        for rec in self:
            location_dest_id = rec.move_line_ids.filtered(lambda pro: pro.location_dest_id.id == rec.truck_id.location_dest_id.id)
            rec.total_qty = sum(location_dest_id.mapped('qty_done'))

    def unlink(self):
        if any(cartoon.total_qty > 0 for cartoon in self):
            raise UserError(_("You can not delete the Cartoon which contains the done Quantity."))
        return super().unlink()


class DNCNProductDetails(models.TransientModel):
    _name = "cn.product.details"
    _description = "DN CN Product Details List"

    product_id = fields.Many2one('product.product', string='Product',)
    available_qty = fields.Float(string='Available Quantity')
    total_qty = fields.Float(string='Total Quantity')
