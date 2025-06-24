from odoo import models, fields, api


class IpdForm(models.Model):
    _inherit = "ipd.registration"

    diet_count = fields.Integer(compute='_compute_diet_count', string='Diet Count')

    # create smart button of diet
    def custom_function(self):
        return {
            'name': 'Diet',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'res_model': 'kitchen.details',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    @api.depends('patient_id')
    def _compute_diet_count(self):
        Diet = self.env['kitchen.details']
        for ipd_form in self:
            ipd_form.diet_count = Diet.search_count([('patient_id', '=', ipd_form.patient_id.id)])
