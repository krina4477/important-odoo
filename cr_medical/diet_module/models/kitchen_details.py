from odoo import models, fields, api
from datetime import timedelta


class KitchenDetails(models.Model):
    _name = "kitchen.details"
    _description = "Kitchen Department"
    _rec_name = "patient_id"

    break_fast_ids = fields.Many2many("break.fast", string="Breakfast")
    lunch_ids = fields.Many2many("lunch.info", string="Lunch")
    dinner_ids = fields.Many2many("dinner.info", string="Dinner")
    patient_id = fields.Many2one('res.partner', string='Patient Name', domain=[('is_patient', '=', True)])
    date_of_admit = fields.Date("Date")
    doctor_department_id = fields.Many2one('doctor.department', string="Doctor Department")
