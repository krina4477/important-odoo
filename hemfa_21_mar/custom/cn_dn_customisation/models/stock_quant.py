# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare, float_is_zero


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    cartoon_id = fields.Many2one('cn.tracking.number', string='To Cartoon')
    truck_id = fields.Many2one('dn.tracking.number', string='To Delivery Number')
    dn_lot_name = fields.Char("DN Lot Name")
    dn_cartoon_id = fields.Many2one('cn.tracking.number', 'Carton Number', copy=False)
    dn_truck_id = fields.Many2one('dn.tracking.number', string='Delivery Number', copy=False)

    @api.onchange('cartoon_id')
    def _onchange_cartoon_id(self):
        if self.cartoon_id and self.truck_id:
            move_line = self.cartoon_id.move_line_ids.filtered(lambda m: m.product_id == self.product_id)
            if move_line and move_line.lot_id:
                self.lot_id = move_line.lot_id

    @api.model
    def _get_inventory_fields_write(self):
        res = super()._get_inventory_fields_write()
        res += ['cartoon_id', 'truck_id']
        return res

    @api.onchange('product_id', 'location_id')
    def _onchange_dn_product_location_id(self):
        self.truck_id = False
        self.cartoon_id = False
        self.lot_id = False

    @api.onchange('truck_id')
    def _onchange_dn_truck_id(self):
        self.cartoon_id = False
        self.lot_id = False

    @api.onchange('cartoon_id')
    def _onchange_dn_lot_id(self):
        self.lot_id = False
        if self.cartoon_id and self.product_id:
            product_in_cn_id = self.cartoon_id.move_line_ids.filtered(lambda ml: ml.product_id == self.product_id)
            if product_in_cn_id:
                self.lot_id = product_in_cn_id.lot_id
            else:
                serial_numbers = self.env['stock.lot'].create({
                    'name': self.truck_id.name + "-" + self.cartoon_id.name,
                    'product_id': self.product_id.id,
                    'company_id': self.env.company.id,
                })
                self.lot_id = serial_numbers

    def _apply_inventory(self):
        for quant in self:
            if quant.truck_id and quant.cartoon_id:
                super(StockQuant, quant.with_context(is_dn_number=quant.truck_id.id, is_cartoon_id=quant.cartoon_id.id))._apply_inventory()
                continue
            super(StockQuant, quant)._apply_inventory()

    @api.model
    def _get_quants_action(self, domain=None, extend=False):
        res = super()._get_quants_action(domain, extend)
        if self._context.get("is_cn_dn_stock"):
            res.update({'name': _('DN/CN Locations'),})
        return res

    def _load_records_create(self, values):
        for val in values:
            if self._name == 'stock.quant' and self.env.context.get('import_file') and val.get('cartoon_id') and val.get('truck_id') and val.get('product_id') and not val.get('lot_id'):
                val.get('truck_id')
                trk_id = self.env['dn.tracking.number'].browse(val.get('truck_id'))
                crtn_id = self.env['cn.tracking.number'].browse(val.get('cartoon_id'))
                cartoon = trk_id.cartoon_ids.filtered(lambda cn: cn.name == crtn_id.name)
                is_cartoon_id = cartoon and cartoon[0] or False
                if is_cartoon_id:
                    val['cartoon_id'] = is_cartoon_id.id
                    product_in_cn_id = is_cartoon_id.move_line_ids.filtered(lambda ml: ml.product_id.id == val.get('product_id'))
                    if product_in_cn_id:
                        val['lot_id'] = product_in_cn_id.lot_id.ids[0]
                    else:
                        serial_numbers = self.env['stock.lot'].create({
                            'name': is_cartoon_id.truck_id.name + "-" + is_cartoon_id.name,
                            'product_id': val.get('product_id'),
                            'company_id': self.env.company.id,
                        })
                        val['lot_id'] = serial_numbers.id
                else:
                    val['cartoon_id'] = False
        return self.create(values)

    @api.model
    def _update_available_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, in_date=None):
        """ Increase or decrease `reserved_quantity` of a set of quants for a given set of
        product_id/location_id/lot_id/package_id/owner_id.

        :param product_id:
        :param location_id:
        :param quantity:
        :param lot_id:
        :param package_id:
        :param owner_id:
        :param datetime in_date: Should only be passed when calls to this method are done in
                                 order to move a quant. When creating a tracked quant, the
                                 current datetime will be used.
        :return: tuple (available_quantity, in_date as a datetime)
        """
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True)
        if lot_id and quantity > 0:
            quants = quants.filtered(lambda q: q.lot_id)

        if location_id.should_bypass_reservation():
            incoming_dates = []
        else:
            incoming_dates = [quant.in_date for quant in quants if quant.in_date and
                              float_compare(quant.quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0]
        if in_date:
            incoming_dates += [in_date]
        # If multiple incoming dates are available for a given lot_id/package_id/owner_id, we
        # consider only the oldest one as being relevant.
        if incoming_dates:
            in_date = min(incoming_dates)
        else:
            in_date = fields.Datetime.now()

        quant = None
        if quants:
            # see _acquire_one_job for explanations
            self._cr.execute("SELECT id FROM stock_quant WHERE id IN %s ORDER BY lot_id LIMIT 1 FOR NO KEY UPDATE SKIP LOCKED", [tuple(quants.ids)])
            stock_quant_result = self._cr.fetchone()
            if stock_quant_result:
                quant = self.browse(stock_quant_result[0])

        if quant:
            if self._context.get('branch'):
                quant.write({
                    'quantity': quant.quantity + quantity,
                    'in_date': in_date,
                    'branch_id':self._context.get('branch'),
                    'dn_truck_id':self._context.get('dn_truck_id') or quant.dn_truck_id.id,
                    'dn_cartoon_id':self._context.get('dn_cartoon_id') or quant.dn_cartoon_id.id,
                    'truck_id':self._context.get('dn_truck_id') or quant.dn_truck_id.id,
                    'cartoon_id':self._context.get('dn_cartoon_id') or quant.dn_cartoon_id.id,
                })
            else:
                quant.write({
                    'quantity': quant.quantity + quantity,
                    'in_date': in_date,
                    'dn_truck_id':self._context.get('dn_truck_id') or quant.dn_truck_id.id,
                    'dn_cartoon_id':self._context.get('dn_cartoon_id') or quant.dn_cartoon_id.id,
                    'truck_id':self._context.get('dn_truck_id') or quant.dn_truck_id.id,
                    'cartoon_id':self._context.get('dn_cartoon_id') or quant.dn_cartoon_id.id
                })                
        else:
            if self._context.get('branch'):
                self.create({
                    'product_id': product_id.id,
                    'location_id': location_id.id,
                    'quantity': quantity,
                    'lot_id': lot_id and lot_id.id,
                    'package_id': package_id and package_id.id,
                    'owner_id': owner_id and owner_id.id,
                    'in_date': in_date,
                    'branch_id':self._context.get('branch'),
                    'dn_truck_id':self._context.get('dn_truck_id'),
                    'dn_cartoon_id':self._context.get('dn_cartoon_id'),
                    'truck_id':self._context.get('dn_truck_id'),
                    'cartoon_id':self._context.get('dn_cartoon_id'),
                })
            else:
                self.create({
                    'product_id': product_id.id,
                    'location_id': location_id.id,
                    'quantity': quantity,
                    'lot_id': lot_id and lot_id.id,
                    'package_id': package_id and package_id.id,
                    'owner_id': owner_id and owner_id.id,
                    'in_date': in_date,
                    'dn_truck_id':self._context.get('dn_truck_id'),
                    'dn_cartoon_id':self._context.get('dn_cartoon_id'),
                    'truck_id':self._context.get('dn_truck_id'),
                    'cartoon_id':self._context.get('dn_cartoon_id')
                })                
        return self._get_available_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=False, allow_negative=True), in_date

