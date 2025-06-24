from odoo import models, _, fields, api


class IpdRegistration(models.Model):
    _inherit = 'ipd.registration'

    surgery_count = fields.Integer(compute="_compute_surgery_count")

    def surgery(self):
        context = {
            'default_patient_id': self.patient_id.id if self and self.patient_id else False, }
        return {
            'name': 'IPD Surgery',
            'type': 'ir.actions.act_window',
            'res_model': 'ipd.surgery',
            'view_mode': 'form',
            'view_id': self.env.ref('surgery.ipd_surgery_view_form').id,
            'target': 'new',
            'context': context,
        }

    def show_patient_surgery(self):
        surgery_tree_view_id = self.env.ref('surgery.show_ipd_surgery_view_tree').id
        surgery_form_view_id = self.env.ref('surgery.show_patient_ipd_surgery_view_form').id
        return {
            'name': _('Surgery'),
            'res_model': 'show.ipd.surgery',
            'view_mode': 'list,form',
            'context': {},
            'domain': [('ipd_id', '=', self.id)],
            'views': [(surgery_tree_view_id, 'tree'), (surgery_form_view_id, 'form')],
            'target': 'current',
            'type': 'ir.actions.act_window',
        }

    @api.depends('patient_id')
    def _compute_surgery_count(self):
        obj = self.env['show.ipd.surgery']
        for surgery in self:
            surgery.surgery_count = obj.search_count([('ipd_id', '=', surgery.id)])
