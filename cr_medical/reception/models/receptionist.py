# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from datetime import date
from datetime import datetime


class ResPartner(models.Model):
    _inherit = "res.partner"

    sex = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Sex')
    is_receptionist = fields.Boolean('Is Receptionist')
    user_id = fields.Many2one('res.users', string='User Id')
    state = fields.Selection(
        [('draft', 'Draft'), ("pending", "Pending"), ("approve", "Approved"), ("reject", "Rejected")],
        string="State", default="draft")


    def create_receptionist_user(self):
        self.state = 'approve'
        for user in self:
            values = {'partner_id': user.id,
                      'name': user.name,
                      # 'groups_id': [(6, 0, [self.env.ref('cr_medical_base.group_patient').id,
                      #                       self.env.ref('base.group_user').id])],
                      # 'groups_id': self.env.ref('base.group_portal'),
                      'login': user.email,

                      }

            res = self.env['res.users'].sudo().create(values)
            # res.sudo().action_reset_password()
            self.user_id = res.id
            return res

    def pending(self):
        self.state = 'pending'

    def cancel(self):
        self.state = 'reject'
