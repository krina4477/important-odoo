# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class UpdatePharmacyStock(models.TransientModel):
    _name = 'update.pharmacy.stock'
    _description = "Update Pharmacy Stock"

    def _get_default_medicine_lines(self):
        ctx = self._context.copy()
        lst = []
        if self._context and self._context.get('medicine_ids'):
            for medicine_id in self._context['medicine_ids']:
                medicine = self.env['product.product'].browse(medicine_id)
                tpl = (0, 0, {'product_id': medicine.id, 'uom_id': medicine.uom_id.id, 'quantity': 0.00})
                lst.append(tpl)
        return lst

    medicine_lines = fields.One2many('update.pharmacy.stock.line', 'pharmacy_stock_id', 'Lines',
                                     default=_get_default_medicine_lines)
    prescription_id = fields.Many2one('pharmacy.prescription', 'Prescription',
                                      default=lambda self: self.env.context.get('active_id'))

    def update_stock(self):
        # Create Customer Delivery
        outgoing_shipment = self.env['stock.picking'].create({
            'partner_id': self.prescription_id.opd_id.patient_id.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        })
        for line in self.medicine_lines:
            if line.quantity:
                if line.product_id.type == 'product' and line.product_id.virtual_available < line.quantity:
                    raise UserError(_("No Stock Available For product %s") % line.product_id.name)

                moves = self.env['stock.move'].create({
                    'name': 'a move',
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': outgoing_shipment.id,
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': self.env.ref('stock.stock_location_customers').id})

        # Assign this outgoing shipment and process the delivery
        aa = outgoing_shipment.action_assign()
        self.env['stock.immediate.transfer'].create({'pick_ids': [(4, outgoing_shipment.id)]}).process()
        self.prescription_id.state = 'done'
        return True


class UpdatePharmacyStockLine(models.TransientModel):
    _name = 'update.pharmacy.stock.line'
    _description = "Pharmacy Stock"

    pharmacy_stock_id = fields.Many2one('update.pharmacy.stock', 'Pharmacy Stock')

    product_id = fields.Many2one('product.product', 'Medicine')
    uom_id = fields.Many2one('uom.uom', 'Unit Of Measure')
    quantity = fields.Float('Quantity')
