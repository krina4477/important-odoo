from odoo import models, fields


class IpdPhysiotherapy(models.TransientModel):
    _name = 'ipd.physiotherapy'
    _description = "IPD Physiotherapy"
    # _rec_name = "name"

    date_of_admit = fields.Date('Date Of Physiotherapy', readonly="True")
    doctor_id = fields.Many2one('res.partner', string="Physiotherapists",
                                domain=[('is_doctor', '=', True), ('doctor_department_id', '=', 'Physiotherapy')],
                                store=True, required=True)
    physiotherapy_exercise = fields.Text(string="Physiotherapy Exercise")
    patient_id = fields.Many2one('res.partner', string='Patient Name', readonly="True",
                                 domain=[('is_patient', '=', True)], store=True)
    ipd_id = fields.Many2one('ipd.registration')

    def _default_date_of_admit(self):
        return self.env.context.get('default_date_of_admit', False)

    def _default_patient_id(self):
        return self.env['res.partner'].browse(
            self.env.context.get('default_patient_id')).display_name if self.env.context.get(
            'default_patient_id') else False

    def patient_Physiotherapy(self):
        physiotherapy_obj = self.env["show.ipd.physiotherapy"]
        # active_id = self._context.get('params').get('id')

        for rec in self:
            physiotherapy_obj.create({
                'date_of_admit': rec.date_of_admit,
                'patient_id': rec.patient_id.id,
                'doctor_id': rec.doctor_id.id,
                'physiotherapy_exercise': rec.physiotherapy_exercise,
                # 'ipd_id': active_id,
            })
