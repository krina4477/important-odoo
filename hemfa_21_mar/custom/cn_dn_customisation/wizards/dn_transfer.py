from odoo import _, models, fields, api
from odoo.fields import Command

class TransferWholeDN(models.TransientModel):
    _name = 'transfer.whole.dn'
    _description = "Transfer Whole DN"

    dn_id = fields.Many2one('dn.tracking.number', string='Delivery Number', copy=False)
    partner_id = fields.Many2one(
        'res.partner', 'Contact',
        check_company=True, required=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, index=True, domain=[('code', '=', 'internal'), ])
    location_id = fields.Many2one(
        'stock.location', "Source Location", store=True, precompute=True,
        check_company=True, required=True, readonly=True)
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        store=True, precompute=True, readonly=False,
        check_company=True, required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', related='picking_type_id.company_id',
        readonly=True, store=True, index=True)

    transit_location_id = fields.Many2one('stock.location', string='Transit Location', domain=[('usage', '=', 'transit')])
    is_two_step_transfer = fields.Boolean(string='Two-Step Transfer')

    def action_full_dn_transfer(self):
        StockMove = self.env['stock.move']
        StockMoveLine = self.env['stock.move.line']
        StockPicking = self.env['stock.picking']
        vals = {
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'is_skip_immediate': True,
            'transit_location_id': self.transit_location_id.id,
            'is_two_step_transfer': self.is_two_step_transfer,
            'whole_dn_id': self.dn_id.id
        }
        stock_picking_id = StockPicking.with_context(default_dn_id=False).create(vals)
        product_list = []
        for line in self.dn_id.cn_product_detail_ids:
            product_dict = {
                'product_id': line.product_id.id,
                'name': line.product_id.partner_ref,
                'product_uom_qty': line.available_qty,
                'picking_id': stock_picking_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id
                }
            product_list.append(product_dict)
        move_ids = StockMove.create(product_list)
        move_ids._compute_reserved_availability()
        stock_picking_id.action_confirm()
        previous_lines = move_ids.move_line_ids
        vals_list = self._prepare_move_lines(move_ids, stock_picking_id)
        StockMoveLine.create(vals_list)
        StockMoveLine.compute_cartoon_lot_ids()
        previous_lines.unlink()
        StockMoveLine._compute_reserved_qty()
        stock_picking_id.move_line_ids = StockMoveLine.ids
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        action['domain'] = [('id', 'in', stock_picking_id.ids)]
        action['context'] = {"is_full_dn_transfer": True}
        return action

    def _prepare_move_lines(self, move_ids, stock_picking_id):
        vals_list = []

        for cn_line in self.dn_id.cartoon_ids:
            cn_id = self.action_generate_cn(stock_picking_id)
            for move_line in cn_line.move_line_ids.filtered(lambda ml: ml.location_dest_id == self.location_id):
                cn_move_id = move_ids.filtered(lambda move: move.product_id.id == move_line.product_id.id)
                if self.is_two_step_transfer and self.transit_location_id.usage in ['internal', 'transit']:
                    lot_name = stock_picking_id.dn_id.name + "-" + cn_id.name + "-Transit"
                else:
                    lot_name = stock_picking_id.dn_id.name + "-" + cn_id.name
                vals = {
                    'move_id': cn_move_id.id,
                    'product_id': move_line.product_id.id,
                    'product_uom_id': move_line.product_id.uom_id.id,
                    'dn_lot_id': move_line.lot_id.id,
                    'location_id': cn_move_id.location_id.id,
                    'location_dest_id': cn_move_id.location_dest_id.id,
                    'from_cartoon_number': cn_line.id,
                    'sale_truck_id': self.dn_id.id,
                    'qty_done': move_line.available_cartoon_qty,
                    'cartoon_id': cn_id.id or False,
                    'lot_name': lot_name,
                    'picking_id': stock_picking_id.id
                }
                vals_list.append(vals)
        return vals_list

    def action_generate_cn(self, stock_picking_id):
        cn_list = []
        if stock_picking_id.dn_id:
            sequence = self.env.ref("cn_dn_customisation.sequence_generate_cn")
            sequence.number_next_actual = len(stock_picking_id.dn_id.cartoon_ids) + 1
            cn_number = self.env['ir.sequence'].next_by_code('generate.cn.number') or '/'
            cn_list.append({
                'name': cn_number,
                'truck_id': stock_picking_id.dn_id.id,
            })
        cn_id = self.env['cn.tracking.number'].create(cn_list)
        return cn_id
