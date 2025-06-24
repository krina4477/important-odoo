from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ShowIpdSurgery(models.TransientModel):
    _name = 'show.ipd.surgery'
    _description = "IPD Surgery"
    _rec_name = "patient_id"

    surgery_date = fields.Date(string="Surgery Date", store=True, required=True, )
    surgery_id = fields.Many2one('surgery.type', string="Surgery", store=True, required=True)
    start_time = fields.Datetime(string="Start Time", widget="time", store=True, required=True,
                                 domain="[('surgery_date', '=', surgery_date)]")
    end_time = fields.Datetime(string="End Time", widget="time", store=True, required=True)
    doctor_id = fields.Many2one('res.partner', string="Special Surgen",
                                domain=[('is_doctor', '=', True), ('doctor_department_id', '=', 'Surgery')], store=True,
                                required=True)
    anesthetic_id = fields.Many2one('res.partner', string="Anesthetic", domain=[('is_doctor', '=', True)], store=True, )
    state = fields.Selection([('draft', 'Draft'), ('progress', 'In Progress'),
                              ('done', 'Done')], default='draft', string="Status", store=True)
    doctor_remark = fields.Char(string="Doctor Remark", store=True)
    ot_remark = fields.Char(string="OT Remark", store=True)
    action = fields.Char(string="Action", store=True)
    patient_id = fields.Many2one('res.partner', string='Patient Name', domain=[('is_patient', '=', True)])
    ipd_id = fields.Many2one('ipd.registration')
    user_id = fields.Many2one('res.users', string='User Id')

    def draft(self):
        self.state = 'draft'

    def progress(self):
        self.state = 'progress'

    def done(self):
        self.state = 'done'

    @api.constrains('surgery_date', 'start_time')
    def _check_surgery_date(self):
        for record in self:
            if record.surgery_date < datetime.today().date():
                raise ValidationError("Surgery Date cannot be in the past.")

            if record.surgery_date and record.start_time:
                surgery_date = fields.Date.from_string(record.surgery_date)
                start_time_date = fields.Datetime.from_string(record.start_time).date()

                if surgery_date != start_time_date:
                    raise ValidationError("Start Time must be on the same day as the Surgery Date.")

    @api.constrains('start_time', 'end_time')
    def _check_time_constraint(self):
        for record in self:
            if record.end_time <= record.start_time:
                raise ValidationError("End time must be greater than start time.")

    @api.constrains('doctor_id', 'anesthetic_id')
    def _check_different_doctors(self):
        for record in self:
            if record.doctor_id and record.anesthetic_id and record.doctor_id == record.anesthetic_id:
                raise ValidationError("Special Surgeon and Anesthetic cannot be the same person.")
