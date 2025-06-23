# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    branch_ids = fields.Many2many('res.branch', string="Branches")


    parent_branch_ids = fields.Many2many(
        'res.branch',
        'res_branch_analytic_plan_rel',
        'branch_id',
        'plan_id',
        compute='_compute_branch_ids',
        store=True,
        string='Parent Branches'
    )


    def write(self, vals):
        res = super().write(vals)
        if vals.get('branch_ids'):
            if not self.branch_ids:
                sub_plans = self.env['account.analytic.plan'].search([('parent_id', '=', self.id)])
                if sub_plans:
                    sub_plans.write({
                        'branch_ids': False
                    })
            sub_plans = self.env['account.analytic.plan'].search([('parent_id', '=', self.id)])
            sub_accounts = self.env['account.analytic.account'].search([('plan_id', '=', self.id)])

            for branch in sub_plans.branch_ids:
                if branch.id not in self.branch_ids.ids:

                    product = sub_plans.filtered(lambda j: j.branch_ids and branch.id in j.branch_ids.ids)
                    if product:
                        for i in product:
                            branch_ids = i.branch_ids.ids
                            branch_ids.remove(branch.id)
                            if not branch_ids:
                                branch_ids = False
                            i.write({
                                'branch_ids': branch_ids
                            })
            for acc_account in sub_accounts.branch_ids:
                if acc_account.id not in self.branch_ids.ids:

                    account = sub_accounts.filtered(lambda j: j.branch_ids and acc_account.id in j.branch_ids.ids)
                    if account:
                        for acc in account:
                            branch_ids = acc.branch_ids.ids
                            branch_ids.remove(acc_account.id)
                            if not branch_ids:
                                branch_ids = False
                            acc.write({
                                'branch_ids': branch_ids
                            })
        return res


    @api.depends('parent_id.branch_ids')
    def _compute_branch_ids(self):
        for rec in self:
            rec.parent_branch_ids = self.env['res.branch'].search([]).ids
            if rec.parent_id and rec.parent_id.branch_ids:
                rec.parent_branch_ids = rec.parent_id.branch_ids.ids


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    branch_ids = fields.Many2many('res.branch', string="Branches")


    parent_branch_ids = fields.Many2many(
        'res.branch',
        'res_branch_analytic_account_rel',
        'branch_id',
        'plan_id',
        compute='_compute_branch_ids',
        store=True,
        string='Parent Branches'
    )

    @api.depends('plan_id.branch_ids')
    def _compute_branch_ids(self):
        for rec in self:
            rec.parent_branch_ids = self.env['res.branch'].search([]).ids
            if rec.plan_id and rec.plan_id.branch_ids:
                rec.parent_branch_ids = rec.plan_id.branch_ids.ids
