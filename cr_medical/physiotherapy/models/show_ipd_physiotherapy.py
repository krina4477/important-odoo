from odoo import models, fields


class IpdPhysiotherapy(models.Model):
    _name = 'show.ipd.physiotherapy'
    _rec_name = "patient_id"

    # name = fields.Char('Seq')
    date_of_admit = fields.Date('Date Of Physiotherapy')
    doctor_id = fields.Many2one('res.partner', string="Physiotherapists",
                                domain=[('is_doctor', '=', True), ('doctor_department_id', '=', 'Physiotherapy')],
                                store=True)
    physiotherapy_exercise = fields.Text(string="Physiotherapy Exercise")
    patient_id = fields.Many2one('res.partner', string='Patient Name',
                                 domain=[('is_patient', '=', True)], store=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('cancelled', 'Cancelled')], default='draft',
                             string="Status",
                             store=True)
    ipd_id = fields.Many2one('ipd.registration')
    summary_id = fields.Many2one('')

    def draft(self):
        self.state = 'draft'

    def done(self):
        self.state = 'done'

    def cancelled(self):
        self.state = 'cancelled'
