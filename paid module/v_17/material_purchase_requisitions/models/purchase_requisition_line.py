# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class MaterialPurchaseRequisitionLine(models.Model):
    _name = "material.purchase.requisition.line"
    _description = 'Material Purchase Requisition Lines'


    requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisitions', 
    )
    task_id = fields.Many2one(comodel_name="project.task", string="Notification", related='requisition_id.task_id')
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    qty = fields.Float(
        string='Quantity',
        default=1,
        required=True,
    )
    uom = fields.Many2one(
        'uom.uom',#product.uom in odoo11
        string='Unit of Measure',
        related='product_id.uom_id'
    )
    state = fields.Selection(
        related='requisition_id.state',
    )
    partner_id = fields.Many2many(
        'res.partner',
        string='Vendors'
    )
    requisition_type = fields.Selection(
        selection=[
                    ('internal','Internal Picking'),
                    ('purchase','Purchase Order'),
        ],
        string='Requisition Action',
        default='purchase',
        required=True,
    )

    onhand = fields.Float(string="Onhand", compute="get_onhand", digits='Product Unit of Measure')
    contact_partner_id = fields.Many2one('res.partner',string="Partner")

    @api.depends('product_id', 'requisition_id.location_id', 'requisition_id', 'uom')
    def get_onhand(self):
        for record in self:
            obj = self.env['stock.quant'].search(
                [('product_id', '=', record.product_id.id),
                 ('location_id', '=', record.requisition_id.location_id.id)])
            amount = 0
            if obj:
                for line in obj:
                    amount += line.quantity
            final_amount = record.product_id.uom_id._compute_quantity(amount, record.uom)
            record.onhand = final_amount

    @api.onchange('product_id')
    def onchange_product_id(self):
        self._product_id_change()
        for rec in self:
            rec.description = rec.product_id.name

    def _product_id_change(self):
        if not self.product_id:
            return

        self.uom = self.product_id.uom_id

