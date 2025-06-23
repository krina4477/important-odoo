# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    branch_ids = fields.Many2many('res.branch')


    def get_product_branch_id(self, branch):
        if self.env['stock.location'].search([('warehouse_id', '=', self.id)]):
            branch_ids = []
            for location in self.env['stock.location'].search([('warehouse_id', '=', self.id)]):
                for branch in location.branch_ids:
                    if branch.id not in branch_ids:
                        branch_ids.append(branch.id)
            if int(branch) in branch_ids:
                return True
            else:
                return False
        else:
            return False


    def write(self, vals):
        res = super().write(vals)
        if vals.get('branch_ids'):
            locations = self.env['stock.location'].search([('warehouse_id', '=', self.id)])
            if not self.branch_ids:
                if locations:
                    locations.write({
                        'branch_ids': False
                    })
            for branch in locations.branch_ids:
                if branch.id not in self.branch_ids.ids:

                    product = locations.filtered(lambda j: j.branch_ids and branch.id in j.branch_ids.ids)
                    if product:
                        for i in product:
                            branch_ids = i.branch_ids.ids
                            branch_ids.remove(branch.id)
                            if not branch_ids:
                                branch_ids = False
                            i.write({
                                'branch_ids': branch_ids
                            })
        return res


    @api.model
    def default_get(self, default_fields):
        res = super(StockWarehouse, self).default_get(default_fields)
        branch_ids = False
        if self._context.get('branch_ids'):
            branch_ids = self._context.get('branch_id')
        elif self.env.user.branch_ids:
            branch_ids = self.env.user.branch_ids.ids

        if 'branch_ids' in default_fields:
            res.update({
                'branch_ids':branch_ids,
            })
        return res

    # @api.onchange('branch_id')
    # def _onchange_branch_id(self):
    #     selected_brach = self.branch_id
    #     if selected_brach:
    #         user_id = self.env['res.users'].browse(self.env.uid)
    #         user_branch = user_id.sudo().branch_id
    #         if user_branch and user_branch.id != selected_brach.id:
    #             raise UserError("Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.")
    #

class StockPickingTypeIn(models.Model):
    _inherit = 'stock.picking.type'

    branch_id = fields.Many2one('res.branch', compute='_compute_branch_ids', store=True)


    @api.depends('warehouse_id.branch_ids')
    def _compute_branch_ids(self):
        for rec in self:
            if rec.warehouse_id.branch_ids:
                rec.branch_id = rec.warehouse_id.branch_ids[0].id
            else:
                rec.branch_id = False
