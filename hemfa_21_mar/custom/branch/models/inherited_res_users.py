# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    branch_ids = fields.Many2many('res.branch', string="Allowed Branch")
    branch_id = fields.Many2one('res.branch', string= 'Branch')
    res_branch_ids = fields.Many2many("res.branch","custom_branch_ids", string="ooooooooo", invisible=True)

    def write(self, values):
        if 'branch_ids' in values:
            self.partner_id.branch_ids = False
            print("========", values)
            self.partner_id.branch_ids = values.get('branch_ids')[0][-1]
        self.env['ir.model.access'].call_cache_clearing_methods()
        return super(ResUsers, self).write(values)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.branch_ids:
            res.partner_id.branch_ids = False
            res.partner_id.branch_ids = res.branch_ids.ids
        return res

    @api.constrains('branch_id', 'branch_ids', 'active')
    def _check_branch(self):
        if self._context.get('params', {}).get('model') == 'res.users':
            for user in self.filtered(lambda u: u.active):
                if user.branch_id and user.branch_id not in user.branch_ids:
                    raise ValidationError(
                        _('Branch %(branch_name)s is not in the allowed branches for user %(user_name)s (%(branch_allowed)s).',
                        branch_name=user.branch_id.name,
                        user_name=user.name,
                        branch_allowed=', '.join(user.mapped('branch_ids.name')))
                    )

    def get_branch_ids(self, availablecompany, currentcompany):
        print("-===============", availablecompany)
        branch_ids = self.env['res.branch'].sudo().search([('company_id', 'in', availablecompany)])
        user_id = self.env['res.users'].sudo().search([('id', '=', self.env.user.id)])
        print("=======33333333333333333333333",user_id.branch_ids)
        if not branch_ids:
            user_id.branch_id = []
        if user_id:
            if user_id.branch_ids:
                branch_ids = user_id.branch_ids
            elif not branch_ids:
                user_id.branch_ids = []
        print("==============3344444444444444444", branch_ids)
        val = {
            'branch_ids': branch_ids.ids,
            'current_branch': self.branch_id.id,
            'company_id': self.company_id.id,
            'allowed_branch_ids': {
                comp.id: {
                    'id': comp.id,
                    'name': comp.name,
                    'company': comp.company_id.id,
                } for comp in branch_ids
            },
            'currentCompanyId': True if currentcompany['id'] == branch_ids.company_id.ids else False,
        }
        print("=========111123445556666666", val)
        return val

    def switch_company_menu(self, company_id):
        user_id = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        allowed_branches = company_id.get("id")
        print("======================22224dfdfffdfdd")
        if user_id.branch_id:
            print("=====111111133345323232323")
            user_id.sudo().write({
                'branch_id': allowed_branches
            })
            print("-===111111578888")

    


