# -*- coding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    ipd_line_ids = fields.One2many("ipd.registration", "patient_id", string="IPD History")
    ipd_count = fields.Integer("IPDs", compute="_compute_ipd_count")

    @api.depends('ipd_line_ids')
    def _compute_ipd_count(self):
        for patient in self:
            patient.ipd_count = len(patient.ipd_line_ids)

    def open_ipd_view(self):
        tree_id = self.env.ref('IPD.cr_ipd_registration_tree_view').id
        form_id = self.env.ref('IPD.cr_ipd_registration_form_view').id

        if self.ipd_count == 1:
            return {'type': 'ir.actions.act_window',
                    'name': _('IPD History'),
                    'res_model': 'ipd.registration',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': self.ipd_line_ids.id,
                    'views': [(form_id, 'form')],
                    'domain': [('patient_id', '=', self.id)]
                    }
        else:
            return {'type': 'ir.actions.act_window',
                    'name': _('IPD History'),
                    'res_model': 'ipd.registration',
                    'view_mode': 'tree,form',
                    'views': [(tree_id, 'tree'), (form_id, 'form')],
                    'domain': [('patient_id', '=', self.id)]}
