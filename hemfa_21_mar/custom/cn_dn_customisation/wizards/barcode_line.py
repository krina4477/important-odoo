from odoo import _, models, fields, api
from odoo.fields import Command
from odoo.exceptions import UserError

class StockMoveBarcode(models.TransientModel):
    _name = 'product.stock.move.barcode'
    _inherit = ['barcodes.barcode_events_mixin']

    dn_id = fields.Many2one('dn.tracking.number', string='Delivery Number', readonly=True, copy=False)
    sequence = fields.Integer(string='Sequence', default=0)
    sh_inventory_barcode_scanner_is_last_scanned = fields.Boolean(
        string="Last Scanned?")
    to_cartoon_id = fields.Many2one('cn.tracking.number', 'To Carton', copy=False, required=True)
    move_line_ids = fields.One2many('product.stock.move.line.barcode', 'barcode_move_id', string='Products')
    picking_id = fields.Many2one('stock.picking', 'Picking')
    duplicate_move_line_ids = fields.One2many('product.stock.move.line.barcode', 'barcode_move_id', compute="_compute_barcode_scanned", string='Products')
    is_load_existing_lines = fields.Boolean("Load Existing Lines")
    is_new_cn_required = fields.Boolean(
        string="Required New CN?", default=False)
    create_cn = fields.Integer("Generate Carton")

    @api.onchange('is_new_cn_required')
    def _onchange_is_new_cn_required(self):
        if self.create_cn:
            self.dn_id.generate_cn = self.create_cn
            self.dn_id.action_generate_cn()
            self.create_cn = 0

    @api.onchange('is_load_existing_lines')
    def _onchange_barcode_scanned(self):
        MoveLine = self.env['product.stock.move.line.barcode']
        if self.is_load_existing_lines:
            i = 0
            for line in self.picking_id.move_line_ids:
                vals = {
                    'product_id': line.product_id.id,
                    'qty_done': line.qty_done,
                    'cartoon_id': line.cartoon_id.id,
                    'lot_name': line.lot_name,
                    'sh_inventory_barcode_scanner_is_last_scanned': False,
                    'sequence': i + 1,
                    'sh_barcode': line.sh_barcode
                    }
                self.move_line_ids = [Command.create(vals)]

    @api.depends('to_cartoon_id', 'move_line_ids.qty_done')
    def _compute_barcode_scanned(self):
        for line in self:
            line.duplicate_move_line_ids = False
            if line.to_cartoon_id:
                line.duplicate_move_line_ids = line.move_line_ids.filtered(lambda ml: ml.cartoon_id == line.to_cartoon_id)

    def action_load_products(self):
        StockMove = self.env['stock.move']
        StockMoveLine = self.env['stock.move.line']
        move_lines_vals = []
        all_cn_move_lines = self.move_line_ids
        for line in self.picking_id.move_ids:
            available_lines = all_cn_move_lines.filtered(lambda mo: mo.product_id == line.product_id)
            all_cn_move_lines = all_cn_move_lines - available_lines
            for mo_line in available_lines:
                avail_move_line_ids = line.move_line_ids.filtered(lambda ml: ml.product_id == mo_line.product_id and ml.cartoon_id == mo_line.cartoon_id)
                avail_move_line_id = avail_move_line_ids and avail_move_line_ids[0] or False
                if avail_move_line_id:
                    if self.is_load_existing_lines:
                        avail_move_line_id.qty_done = mo_line.qty_done
                        avail_move_line_id.sh_barcode = mo_line.sh_barcode
                    else:
                        avail_move_line_id.qty_done += mo_line.qty_done
                        avail_move_line_id.sh_barcode = mo_line.sh_barcode
                else:
                    vals = {
                        'move_id': line.id,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_id.uom_id.id,
                        'lot_name': mo_line.lot_name,
                        'location_id': line.location_id.id,
                        'location_dest_id': line.location_dest_id.id,
                        'cartoon_id': mo_line.cartoon_id.id,
                        'qty_done': mo_line.qty_done,
                        'picking_id': self.picking_id.id,
                        'sh_barcode': mo_line.sh_barcode
                    }
                    move_lines_vals.append(vals)
        all_product_line_list = []
        for line in all_cn_move_lines:
            if not all_product_line_list:
                vals = {
                    'product_id': line.product_id.id,
                    'lot_name': line.lot_name,
                    'location_id': self.picking_id.location_id.id,
                    'location_dest_id': self.picking_id.location_dest_id.id,
                    'cartoon_id': line.cartoon_id.id,
                    'qty_done': line.qty_done,
                    'picking_id': self.picking_id.id,
                    'sh_barcode': line.sh_barcode
                }
                product_dict = {
                    'product_id': line.product_id.id,
                    'name': line.product_id.partner_ref,
                    'product_uom_qty': line.qty_done,
                    'picking_id': self.picking_id.id,
                    'location_id': self.picking_id.location_id.id,
                    'location_dest_id': self.picking_id.location_dest_id.id,
                    'move_line_ids': [(0, 0, vals)],
                    }
                all_product_line_list.append(product_dict)
            else:
                for list_line in all_product_line_list:
                    if list_line.get('product_id') and list_line.get('product_id') == line.product_id.id:
                        vals = {
                            'product_id': line.product_id.id,
                            'lot_name': line.lot_name,
                            'location_id': self.picking_id.location_id.id,
                            'location_dest_id': self.picking_id.location_dest_id.id,
                            'cartoon_id': line.cartoon_id.id,
                            'qty_done': line.qty_done,
                            'picking_id': self.picking_id.id,
                            'sh_barcode': line.sh_barcode
                        }
                        list_line['move_line_ids'].append((0, 0, vals))
                        break
                    else:
                        vals = {
                            'product_id': line.product_id.id,
                            'lot_name': line.lot_name,
                            'location_id': self.picking_id.location_id.id,
                            'location_dest_id': self.picking_id.location_dest_id.id,
                            'cartoon_id': line.cartoon_id.id,
                            'qty_done': line.qty_done,
                            'picking_id': self.picking_id.id,
                            'sh_barcode': line.sh_barcode
                        }
                        product_dict = {
                            'product_id': line.product_id.id,
                            'name': line.product_id.partner_ref,
                            'product_uom_qty': line.qty_done,
                            'picking_id': self.picking_id.id,
                            'location_id': self.picking_id.location_id.id,
                            'location_dest_id': self.picking_id.location_dest_id.id,
                            'move_line_ids': [(0, 0, vals)],
                            }
                        all_product_line_list.append(product_dict)
                        break
        move_id = StockMove.create(all_product_line_list)
        # move_id._compute_reserved_availability()
        # self.picking_id.action_confirm()
        StockMoveLine.create(move_lines_vals)
        return True

    def _add_product(self, barcode):
        self.clear_caches()
        if not self.to_cartoon_id:
            raise UserError(_("Select carton number to perform operations."))

        is_last_scanned = False
        sequence = 0
        warm_sound_code = ""
        if self.env.company.sudo().sh_sale_barcode_scanner_last_scanned_color:
            is_last_scanned = True

        if self.env.company.sudo().sh_sale_barcode_scanner_move_to_top:
            sequence = -1

        if self.env.company.sudo().sh_sale_barcode_scanner_warn_sound:
            warm_sound_code = "SH_BARCODE_SCANNER_"

        if self.env.company.sudo().sh_sale_barcode_scanner_auto_close_popup:
            warm_sound_code += "AUTO_CLOSE_AFTER_" + \
                str(self.env.company.sudo(
                ).sh_sale_barcode_scanner_auto_close_popup) + "_MS&"

        elif self:

            self.move_line_ids.update({
                'sh_inventory_barcode_scanner_is_last_scanned': False,
                'sequence': 0,
            })

            search_lines = False
            domain = []
            if self.env.company.sudo().sh_sale_barcode_scanner_type == "barcode":
                search_lines = self.move_line_ids.filtered(
                    lambda ol: ol.product_id.barcode == barcode)
                domain = [("barcode", "=", barcode)]

            elif self.env.company.sudo().sh_sale_barcode_scanner_type == "int_ref":
                search_lines = self.move_line_ids.filtered(
                    lambda ol: ol.product_id.default_code == barcode)
                domain = [("default_code", "=", barcode)]

            elif self.env.company.sudo().sh_sale_barcode_scanner_type == "sh_qr_code":
                search_lines = self.move_line_ids.filtered(
                    lambda ol: ol.product_id.sh_qr_code == barcode)
                domain = [("sh_qr_code", "=", barcode)]

            elif self.env.company.sudo().sh_sale_barcode_scanner_type == "all":
                search_lines = self.move_line_ids.filtered(lambda ol: ol.product_id.barcode == barcode or
                                                        ol.product_id.default_code == barcode or
                                                        ol.product_id.sh_qr_code == barcode
                                                        )
                domain = ["|", "|",
                          ("default_code", "=", barcode),
                          ("barcode", "=", barcode),
                          ("sh_qr_code", "=", barcode)]

            if search_lines and search_lines.filtered(lambda ml: ml.cartoon_id.id == self.to_cartoon_id.id):
                carton_base_ids = search_lines.filtered(lambda ml: ml.cartoon_id.id == self.to_cartoon_id.id)
                carton_search_line = carton_base_ids and carton_base_ids[0] or False
                carton_search_line.qty_done += 1
                carton_search_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                carton_search_line.sequence = sequence
                carton_search_line.sh_barcode = barcode
            else:
                search_product = self.env["product.product"].search(
                    domain, limit=1)
                if not search_product:
                    search_product_barcode = self.env["product.template.barcode"].sudo().search(
                        [('name', '=', barcode),
                         ('available_item', '=', True)
                         ], limit=1)
                    search_product = search_product_barcode.product_id

                product_search_lines = self.move_line_ids.filtered(lambda ol: ol.product_id == search_product and ol.cartoon_id == self.to_cartoon_id)
                if product_search_lines:
                    product_carton_search_line = product_search_lines and product_search_lines[0] or False
                    product_carton_search_line.qty_done += 1
                    product_carton_search_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                    product_carton_search_line.sequence = sequence
                    product_carton_search_line.sh_barcode = barcode
                elif search_product:
                    vals = {
                        'product_id': search_product.id,
                        'qty_done': 1,
                        'sh_inventory_barcode_scanner_is_last_scanned': is_last_scanned,
                        'sequence': sequence,
                        'lot_name': self.dn_id.name + "-" + self.to_cartoon_id.name,
                        'cartoon_id': self.to_cartoon_id,
                        'sh_barcode': barcode
                    }
                    self.move_line_ids = [Command.create(vals)]
                else:
                    raise UserError(
                        _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

    def on_barcode_scanned(self, barcode):
        self._add_product(barcode)


class StockMoveLineBarcode(models.TransientModel):
    _name = 'product.stock.move.line.barcode'

    sequence = fields.Integer(string='Sequence', default=0)
    sh_inventory_barcode_scanner_is_last_scanned = fields.Boolean(
        string="Last Scanned?")
    barcode_move_id = fields.Many2one('product.stock.move.barcode', string='Move')
    product_id = fields.Many2one('product.product', string='Product',)
    qty_done = fields.Float(string='Done Quantity')
    lot_name = fields.Char(string='Lot Name')
    cartoon_id = fields.Many2one('cn.tracking.number', 'To Carton', copy=False)
    sh_barcode = fields.Char(string='SH Barcode')
