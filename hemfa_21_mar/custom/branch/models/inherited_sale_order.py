# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('user_id', 'company_id')
    def _compute_warehouse_id(self):
        for order in self:
            if not order.warehouse_id:
                default_warehouse_id = self.env['ir.default'].with_company(
                    order.company_id.id).get_model_defaults('sale.order').get('warehouse_id')
                if order.state in ['draft', 'sent'] or not order.ids:
                    # Should expect empty
                    if default_warehouse_id is not None:
                        order.warehouse_id = default_warehouse_id
                    else:
                        order.warehouse_id = order.user_id.with_company(order.company_id.id)._get_default_warehouse_id()

    @api.model_create_multi
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        branch_id = warehouse_id = False
        if self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        if branch_id:
            branched_warehouse = self.env['stock.warehouse'].search([('branch_ids', 'in', [branch_id])])
            if branched_warehouse:
                warehouse_id = branched_warehouse.ids[0]

        if not warehouse_id:
            warehouse_id = self.env.user._get_default_warehouse_id()
            warehouse_id = warehouse_id.id

        if 'branch_id' in fields:
            res.update({
                'branch_id': branch_id,
                'warehouse_id': warehouse_id
            })

        return res

    branch_id = fields.Many2one('res.branch', string="Branch")

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['branch_id'] = self.branch_id.id
        if self.branch_id:
            journal = self.env['account.journal'].search(
                [('branch_id', '=', self.branch_id.id), ('type', '=', 'sale')], limit=1)
            if journal:
                res['journal_id'] = journal.id
        return res

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        selected_brach = self.branch_id
        if selected_brach:
            user_id = self.env['res.users'].browse(self.env.uid)
            user_branch = user_id.sudo().branch_id
            if user_branch and user_branch.id != selected_brach.id:
                raise UserError(
                    "Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.")


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    branch_ids = fields.Many2many('res.branch')
