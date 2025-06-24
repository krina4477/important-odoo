from odoo import models, fields


class IpdSurgery(models.TransientModel):
    _name = 'ipd.surgery'
    _description = "IPD Surgery"
    _rec_name = "surgery_id"

    surgery_date = fields.Date(string="Surgery Date", store=True)
    surgery_id = fields.Many2one('surgery.type', string="Surgery", store=True)
    start_time = fields.Datetime(string="Start Time", widget="time", store=True)
    end_time = fields.Datetime(string="End Time", widget="time", store=True)
    doctor_id = fields.Many2one('res.partner', string="Special Surgen",
                                domain=[('is_doctor', '=', True), ('doctor_department_id', '=', 'Surgery')], store=True,
                                required=True)
    anesthetic_id = fields.Many2one('res.partner', string="Anesthetic", domain=[('is_doctor', '=', True)], store=True)
    # state = fields.Selection([('draft', 'Draft'), ('progress', 'In Progress'),
    #                           ('done', 'Done')], default='draft', string="Status", store=True)
    doctor_remark = fields.Char(string="Doctor Remark", store=True)
    ot_remark = fields.Char(string="OT Remark", store=True)
    action = fields.Char(string="Action", store=True)
    # patient_name = fields.Char(string="Patient Name", default=lambda self: self._default_patient_name(), store=True)
    patient_id = fields.Many2one('res.partner', string='Patient Name', readonly="True",
                                 domain=[('is_patient', '=', True)], store=True, )
    ipd_id = fields.Many2one('ipd.registration')

    def _default_patient_id(self):
        return self.env['res.partner'].browse(
            self.env.context.get('default_patient_id')).display_name if self.env.context.get(
            'default_patient_id') else False

    def patient_surgery(self):
        # Create a new record in the ipd.surgery model with the data from the wizard form
        active_id = self._context.get('active_id')
        vals = {
            'patient_id': self.patient_id.id,
            'surgery_date': self.surgery_date,
            'surgery_id': self.surgery_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'doctor_id': self.doctor_id.id,
            'anesthetic_id': self.anesthetic_id.id,
            'doctor_remark': self.doctor_remark,
            'ot_remark': self.ot_remark,
            'action': self.action,
            'state': 'draft',
            'ipd_id': active_id,
        }
        self.env['show.ipd.surgery'].create(vals)

        # return {
        #     'name': 'Ipd Surgery',
        #     'res_model': 'show.ipd.surgery',
        #     'view_mode': 'tree,form',
        #     'res_id': surgery.id,  # Open the newly created surgery record in form view
        #     'type': 'ir.actions.act_window',
        #     'target': 'current',
        # }
