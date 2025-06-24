# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError



class WizardCreateOpd(models.TransientModel):
    _name = 'wizard.create.opd'
    _description = "Create OPD From Wizard"

    appointment_date = fields.Date("Appointment Date")
    weekdays = fields.Char("WeekDay Name")
    select_time_id = fields.Many2one('doctor.weeklyavalibility', string='Select Time')

    @api.onchange("appointment_date")
    def onchange_appointment_date(self):
        active_id = self.env['res.partner'].sudo().browse(self._context.get('active_id'))
        if not active_id.doctor_id:
            raise ValidationError(_("Please Select Doctor."))
        if self.appointment_date:
            self.weekdays = self.appointment_date.strftime("%A")
            week_ids = self.env['weekday.name'].sudo().search([('name', '=', self.appointment_date.strftime("%A"))])
            return {'domain': {
                'select_time_id': [('available_weekdays', 'in', week_ids.ids),
                                   ('doctor_id', '=', active_id.doctor_id.id)]}}

    @api.onchange("appointment_date")
    def onchange_appointment_date_weekday(self):
        self.select_time_id = False
        for rec in self:
            if rec.appointment_date:
                rec.weekdays = rec.appointment_date.strftime("%A")

    def create_opd(self):
        active_id = self.env['res.partner'].sudo().browse(self._context.get('active_id'))
        for rec in self:
            vals = {
                'existing_patient_name': True,
                'patient_id': active_id.id,
                'doctor_department_id': active_id.doctor_department_id.id,
                'doctor_id': active_id.doctor_id.id,
                'appointment_date': rec.appointment_date,
                'weekdays': rec.weekdays,
                'select_time_id': rec.select_time_id.id,
                'sex': active_id.sex,
                'date_of_birth': active_id.date_of_birth,
                'age': active_id.age,
                'blood_group': active_id.blood_group,
                'email': active_id.email,
                'mobile': active_id.mobile,
                'street': active_id.street,
                'street2': active_id.street2,
                'city': active_id.city,
                'zip': active_id.zip,
                'state_id': active_id.state_id.id,
                'country_id': active_id.country_id.id,
                'is_normal_opd': True,
            }
            return self.env['opd.opd'].create(vals)
