from odoo import models, fields


class IpdSummary(models.Model):
    _inherit = 'ipd.summary'

    ipd_id = fields.Many2one('ipd.registration')

    def physiotherapy(self):
        context = {
            'default_date_of_admit': self.date_of_admit,
            'default_patient_id': self.ipd_id.patient_id.id if self.ipd_id and self.ipd_id.patient_id else False,
        }
        return {
            'name': 'IPD Physiotherapy',
            'type': 'ir.actions.act_window',
            'res_model': 'ipd.physiotherapy',
            'view_mode': 'form',
            'view_id': self.env.ref('physiotherapy.ipd_physiotherapy_view_form').id,
            'target': 'new',
            'context': context,
        }
