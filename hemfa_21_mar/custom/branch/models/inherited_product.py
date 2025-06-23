# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductTemplateIn(models.Model):
    _inherit = 'product.template'


    def get_product_branch_id(self, branch):
        if int(branch) in self.product_variant_ids.branch_ids.ids:
            return True
        else:
            return False

    @api.model
    def default_get(self, default_fields):
        res = super(ProductTemplateIn, self).default_get(default_fields)
        if self.env.user.branch_ids:
            if 'branch_ids' in default_fields:
                res.update({
                    'branch_ids': self.env.user.branch_ids.ids or False
                })

        return res

    branch_ids = fields.Many2many('res.branch', string="Branch")

    def write(self, vals):
        res = super().write(vals)
        if vals.get('branch_ids'):
            if not self.branch_ids:
                self.product_variant_ids.write({
                    'branch_ids': False
                })
            for branch in self.product_variant_ids.branch_ids:
                if branch.id not in self.branch_ids.ids:

                    product = self.product_variant_ids.filtered(lambda j: j.branch_ids and branch.id in j.branch_ids.ids)
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


class ProductProduct(models.Model):
    _inherit = 'product.product'

    template_branch_ids = fields.Many2many('res.branch', 'product_branch_branch_rel', 'id', 'branch_id',
                                           string="Branch", related='product_tmpl_id.branch_ids', store=True)
    branch_ids = fields.Many2many('res.branch', 'product_branch_relation_rel', 'id', 'branch_id', string="Branch")
