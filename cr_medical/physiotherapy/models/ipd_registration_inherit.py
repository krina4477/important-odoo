from odoo import models, _, fields, api


class IpdRegistration(models.Model):
    _inherit = 'ipd.registration'

    physiotherapy_count = fields.Integer(compute="_compute_physiotherapy_count")

    def show_patient_physiotherapy(self):
        # pdb.set_trace()
        physiotherapy_tree_view_id = self.env.ref('physiotherapy.show_ipd_physiotherapy_view_tree').id
        physiotherapy_form_view_id = self.env.ref('physiotherapy.show_patient_ipd_physiotherapy_view_form').id
        return {
            'name': _('Physiotherapy'),
            'res_model': 'show.ipd.physiotherapy',
            'view_mode': 'list,form',
            'context': {},
            'domain': [('patient_id', '=', self.patient_id.id)],
            'views': [(physiotherapy_tree_view_id, 'tree'), (physiotherapy_form_view_id, 'form')],
            'target': 'current',
            'type': 'ir.actions.act_window',
        }

    @api.depends('patient_id')
    def _compute_physiotherapy_count(self):
        obj = self.env['show.ipd.physiotherapy']
        for physiotherapy in self:
            physiotherapy.physiotherapy_count = obj.search_count([('patient_id', '=', physiotherapy.patient_id.id)])
