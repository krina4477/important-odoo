# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, _, api
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    sequence = fields.Integer(string='Sequence', default=0)
    sh_inventory_barcode_scanner_is_last_scanned = fields.Boolean(
        string="Last Scanned?")


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ['barcodes.barcode_events_mixin', 'stock.move']

    sequence = fields.Integer(string='Sequence', default=0)
    sh_inventory_barcode_scanner_is_last_scanned = fields.Boolean(
        string="Last Scanned?")

    def on_barcode_scanned(self, barcode):
        is_last_scanned = False
        sequence = 0
        warm_sound_code = ""

        if self.env.company.sudo().sh_inventory_barcode_scanner_last_scanned_color:
            is_last_scanned = True

        if self.env.company.sudo().sh_inventory_barcode_scanner_move_to_top:
            sequence = -1

        if self.env.company.sudo().sh_inventory_barcode_scanner_warn_sound:
            warm_sound_code = "SH_BARCODE_SCANNER_"

        if self.env.company.sudo().sh_inventory_barcode_scanner_auto_close_popup:
            warm_sound_code += "AUTO_CLOSE_AFTER_" + \
                str(self.env.company.sudo(
                ).sh_inventory_barcode_scanner_auto_close_popup) + "_MS&"

        # # =============================
        # # UPDATED CODE
        # move_lines = False
        #
        # # INCOMING
        # # ===================================
        # if self.picking_code in ['incoming']:
        #     move_lines = self.move_line_nosuggest_ids
        #
        # # OUTGOING AND TRANSFER
        # # ===================================
        # elif self.picking_code in ['outgoing', 'internal']:
        #     move_lines = self.move_line_ids

        # 15.0.3
        move_lines = self._get_move_lines()
        # 15.0.3

        # UPDATED CODE
        # =============================
        if self.picking_id.state not in ['confirmed', 'assigned']:
            selections = self.picking_id.fields_get()['state']['selection']
            value = next((v[1] for v in selections if v[0] ==
                          self.picking_id.state), self.picking_id.state)
            raise UserError(
                _(warm_sound_code + "You can not scan item in %s state.") % (value))
        elif move_lines:
            for line in move_lines:
                if self.env.company.sudo().sh_inventory_barcode_scanner_type == 'barcode':
                    if self.product_id.barcode == barcode:
                        similar_lines = move_lines.filtered(
                            lambda ml: ml.product_id.barcode == barcode)
                        len_similar_lines = len(similar_lines)
                        if len_similar_lines:
                            last_line = similar_lines[len_similar_lines - 1]
                            last_line.qty_done += 1
                            last_line._onchange_qty_done()
                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned

                        if self.quantity_done == self.product_uom_qty + 1:
                            warning_mess = {
                                'title': _('Alert!'),
                                'message': warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                            }
                            return {'warning': warning_mess}
                        break
                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                elif self.env.company.sudo().sh_inventory_barcode_scanner_type == 'int_ref':
                    if self.product_id.default_code == barcode:
                        similar_lines = move_lines.filtered(
                            lambda ml: ml.product_id.default_code == barcode)
                        len_similar_lines = len(similar_lines)
                        if len_similar_lines:
                            last_line = similar_lines[len_similar_lines - 1]
                            last_line.qty_done += 1
                            last_line._onchange_qty_done()
                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                        if self.quantity_done == self.product_uom_qty + 1:
                            warning_mess = {
                                'title': _('Alert!'),
                                'message': warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                            }
                            return {'warning': warning_mess}
                        break
                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))
                elif self.env.company.sudo().sh_inventory_barcode_scanner_type == 'sh_qr_code':
                    if self.product_id.sh_qr_code == barcode:
                        similar_lines = move_lines.filtered(
                            lambda ml: ml.product_id.sh_qr_code == barcode)
                        len_similar_lines = len(similar_lines)
                        if len_similar_lines:
                            last_line = similar_lines[len_similar_lines - 1]
                            last_line.qty_done += 1
                            last_line._onchange_qty_done()
                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                        if self.quantity_done == self.product_uom_qty + 1:
                            warning_mess = {
                                'title': _('Alert!'),
                                'message': warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                            }
                            return {'warning': warning_mess}
                        break
                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                elif self.env.company.sudo().sh_inventory_barcode_scanner_type == 'all':
                    if self.product_id.barcode == barcode or self.product_id.default_code == barcode or self.product_id.sh_qr_code == barcode:
                        similar_lines = move_lines.filtered(
                            lambda ml: ml.product_id.barcode == barcode or ml.product_id.default_code == barcode or ml.product_id.sh_qr_code == barcode)
                        len_similar_lines = len(similar_lines)
                        if len_similar_lines:
                            last_line = similar_lines[len_similar_lines - 1]
                            last_line.qty_done += 1
                            last_line._onchange_qty_done()
                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                        if self.quantity_done == self.product_uom_qty + 1:
                            warning_mess = {
                                'title': _('Alert!'),
                                'message': warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                            }
                            return {'warning': warning_mess}
                        break
                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))
        else:
            raise UserError(
                _(warm_sound_code + "Pls add all product items in line than rescan."))
        return
