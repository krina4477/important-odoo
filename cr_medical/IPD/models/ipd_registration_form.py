# -*- coding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class IpdRegistration(models.Model):
    _inherit = "ipd.registration"
    _description = "Registering Inpatient Room"
    _rec_name = "name"

    @api.model  # seq
    def create(self, vals):
        res = super(IpdRegistration, self).create(vals)
        vals['name'] = self.env['ir.sequence'].next_by_code('IPDs')
        res.name = vals['name']
        return res

    def treatment_progress(self):
        self.state = 'in progress'

    def room_allocation(self):
        self.select_room_number.state = 'selected'
        self.state = 'allocated'

    def discharge_patient(self):
        self.state = 'discharge'
        self.select_room_number.state = 'not selected'

    name = fields.Char('Seq')
    patient_id = fields.Many2one('res.partner', string='Patient Name', domain=[('is_patient', '=', True)])
    opd_id = fields.Many2one('opd.opd')
    date_of_admit = fields.Date('Date Of Admission')
    select_room_type = fields.Many2one('room.type', string='Type Of Room')
    select_room_number = fields.Many2one('room', string='Room Number')
    disease = fields.Char(string="Disease")
    doctor_id = fields.Many2one('res.partner', string="Doctor Name", domain=[('is_doctor', '=', True)])
    ipd_summary_line_ids = fields.One2many('ipd.summary', 'ipd_id')
    state = fields.Selection([('draft', 'Draft'), ('in progress', 'In Progress'), ("allocated", "Allocated"),
                              ('discharge', 'Discharge')], default='draft')
    attachment_ids = fields.Many2many('ir.attachment')

    # ref_opd_id = fields.Many2one('opd.opd')

    @api.constrains('date_of_admit')
    def _valid_date_of_admit(self):
        today = date.today()
        if self.date_of_admit < today:
            raise ValidationError('Enter Valid Date Of Admission')


class IpdSummary(models.Model):
    _name = "ipd.summary"
    _description = "Summary Of Inpatient"

    date_of_admit = fields.Date('Date Of Admit')
    disease_indication = fields.Text('Disease Indication')
    doctor_refer_id = fields.Many2one('res.partner', string='Reffered Doctor')
    doctor_department_id = fields.Many2one('doctor.department', string="Doctor Department")
    # medicine_detail = fields.Text('Medicine Details')
    medicine_detail = fields.Many2one('product.product', string="Medicine Details")
    morning_dose = fields.Boolean(string="Morning")
    noon_dose = fields.Boolean(string="Noon")
    evening_dose = fields.Boolean(string="Evening")
    night_dose = fields.Boolean(string="Night")
    # after_before_meal = fields.Boolean(string="A/B meal")
    frequency = fields.Selection([('after meal', 'After Meal'), ('before meal', 'Before Meal')], default='after meal',
                                 string="Frequency")
    dose = fields.Integer(string="Dose")
    medicine_days = fields.Integer("Days/Quantity")
    total_tablets = fields.Float(string="Total Tablets")
    ipd_id = fields.Many2one("ipd.registration")

    @api.onchange('medicine_days', 'dose', 'morning_dose', 'noon_dose', 'evening_dose', 'night_dose')
    def onchange_medicine_days(self):
        total_medicine = 0
        if self.morning_dose:
            total_medicine += 1
        if self.noon_dose:
            total_medicine += 1
        if self.evening_dose:
            total_medicine += 1
        if self.night_dose:
            total_medicine += 1
        if self.medicine_days:
            self.total_tablets = self.dose * self.medicine_days * total_medicine
        if self.dose:
            self.total_tablets = self.dose * self.medicine_days * total_medicine

    @api.onchange('date_of_admit')
    def check_admit_date(self):
        if self.ipd_id and self.date_of_admit:
            if self.date_of_admit < self.ipd_id.date_of_admit:
                raise ValidationError("Enter 'Date Of Admit' Greater than 'Date Of Admission'")

    def abc(self):
        pass


class NumberOfBeds(models.Model):
    _name = "number.of.beds"
    _description = "Number Of Beds"
    _rec_name = "no_of_bed"

    no_of_bed = fields.Integer('Bed Number')
    date_of_admit = fields.Date('Treatment Date')
    disease_indication = fields.Text('Disease Indication')
    doctor_refer_id = fields.Many2one('res.partner', string='Reffered Doctor')
    medicine_detail = fields.Many2one('product.product', string="Medicine Details")
    ipd_id = fields.Many2one("ipd.registration")


class StockQuant(models.Model):
    _inherit = "stock.quant"
    _description = 'Information About stock'

    @api.model
    def _get_inventory_fields_write(self):
        fields = ['inventory_quantity', 'inventory_quantity_auto_apply', 'inventory_diff_quantity',
                  'inventory_date', 'user_id', 'inventory_quantity_set', 'is_outdated', 'product_id']
        return fields
