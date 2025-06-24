# -*- coding: utf-8 -*-
import random
from datetime import date

import requests
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


def random_token():
    chars = '0123456789'
    return ''.join(random.SystemRandom().choice(chars) for _ in range(8))


class opdopd(models.Model):
    _name = "opd.opd"
    _description = "patient can book their appointment"

    @api.onchange('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth and record:
                if str(record.date_of_birth) > str(date.today()):
                    warning_mess = {
                        'title': ('Warning!'),
                        'message': ('Pleace Select Valid Date!!'),
                    }
                    return {'warning': warning_mess}
                else:
                    if record.date_of_birth and record.date_of_birth <= fields.Date.today():
                        years = relativedelta(date.today(), record.date_of_birth).years
                        months = relativedelta(date.today(), record.date_of_birth).months
                        record.age = str(int(years)) + ' Years, ' + str(int(months)) + ' Months '

    def create_new_patient(self):
        self.create_new_patient_button = True
        self.is_new_patient = True
        for user in self:
            values = {
                'name': user.new_patient_name,
                'doctor_id': user.doctor_id.id,
                'doctor_department_id': user.doctor_department_id.id,
                'blood_group': user.blood_group,
                'sex': user.sex,
                'date_of_birth': user.date_of_birth,
                'age': user.age,
                'mobile': user.mobile,
                'email': user.email,
                'is_patient': True,
                'street': user.street,
                'street2': user.street2,
                'country_id': user.country_id.id,
                'state_id': user.state_id.id,
                'city': user.city,
                'zip': user.zip,
                'active': True,
                'marital_status': 'single',
                'state': 'approve'
            }
            res = self.env['res.partner'].sudo().create(values)
            user.patient_id.user_id = res
            user.patient_id = res.id
            tokan = random_token()
            confirmation_ref = tokan + str(res.id)
            res.write({'confirmation_ref': confirmation_ref})
            template = self.env.ref('cr_medical_base.registration_patient_and_appointment')
            template.sudo().update({
                'email_from': self.env.user.company_id.email,
                'email_to': self.email
            })
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            template.with_context(user_name=user.new_patient_name, confirmation_ref=confirmation_ref,
                                  appointment_date=self.appointment_date).sudo().send_mail(res.id, force_send=True)
            return res

    def confirm_appointment(self):
        # if not self.existing_patient_name and not self.new_patient_id:
        #     raise Warning(_('Please create new patient'))
        self.state = "confirm"

    def admitted_patient(self):
        self.state = "admitted"

    def pending_appointment(self):
        self.state = "pending"
        # if self.

    def reject_appointment(self):
        self.state = "cancel"

    def send_appointment(self):
        self.state = 'sent'
        for rec in self.medicine_line_ids:
            product_search = self.env['product.product'].sudo().search(
                [('id', '=', rec.medicine_id.id)])
            for product in product_search:
                if product.is_medicine == True:
                    stock_loc = self.env.ref('stock.stock_location_stock').id
                    quant_id = self.env['stock.quant'].search(
                        [('product_id', '=', product.ids), ('location_id', '=', stock_loc)])
                    if rec.dose > quant_id.available_quantity:
                        raise ValidationError(
                            _("You have insufficient stock (%s)! Please manage stock for medicine - %s")
                            % (quant_id.available_quantity, product.name))

                    move_vals = {
                        'product_id': product.id,
                        'name': 'Pharmacy ' + str(rec.pharmacy_id.name) + '-' + str(rec.pharmacy_id.name),
                        'product_uom_qty': rec.total_tablets,
                        'product_uom': product.uom_id.id,
                        'location_id': stock_loc,
                        'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                        'warehouse_id': 1,
                        'origin': self.opd_id.name,
                    }
                    move_id = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
                    move_id._action_confirm()
                    move_id._action_assign()
                    move_id.move_line_ids.write({'qty_done': rec.total_tablets})
                    move_id._action_done()

        for opd in self:
            if not opd.opd_id:
                opd_id = opd.id
            else:
                opd_id = opd.opd_id.id

            if opd.medicine_line_ids:
                for line in opd.medicine_line_ids:
                    line.sudo().write({
                        'opd_id': opd.id,
                        'ref_opd_id': opd_id,
                        'patient_id': opd.patient_id.id or opd.new_patient_id.id,
                        'doctor_id': opd.doctor_id.id,
                        'prescriptionDate': opd.appointment_date
                    })

            if opd.lab_line_ids:
                for line in opd.lab_line_ids:
                    line.sudo().write({
                        'opd_id': opd.id,
                        'ref_opd_id': opd_id,
                        'patient_id': opd.patient_id.id or opd.new_patient_id.id,
                        'doctor_id': opd.doctor_id.id,
                        'prescriptionDate': opd.appointment_date
                    })

            if opd.radio_line_ids:
                for line in opd.radio_line_ids:
                    line.sudo().write({
                        'opd_id': opd.id,
                        'ref_opd_id': opd_id,
                        'patient_id': opd.patient_id.id or opd.new_patient_id.id,
                        'doctor_id': opd.doctor_id.id,
                        'prescriptionDate': opd.appointment_date
                    })
            if opd.follow_up_date:
                weekday = opd.follow_up_date.strftime("%A")

                vals = {
                    'name': opd.name,
                    'opd_id': opd_id,
                    'patient_id': opd.patient_id.id,
                    'doctor_id': opd.doctor_id.id,
                    'appointment_date': opd.follow_up_date,
                    'doctor_department_id': opd.doctor_department_id.id,
                    'select_time_id': opd.select_time_id.id,
                    'weekdays': weekday,
                    'is_follow_up_opd': True,
                    'is_normal_opd': False,
                    'state': 'confirm',
                    'sex': opd.sex,
                    'date_of_birth': opd.date_of_birth,
                    'age': opd.age,
                    'blood_group': opd.blood_group,
                    'email': opd.email,
                    'mobile': opd.mobile,
                    'street': opd.street,
                    'street2': opd.street2,
                    'city': opd.city,
                    'zip': opd.zip,
                    'state_id': opd.state_id.id,
                    'country_id': opd.country_id.id,
                }
                self.env['opd.opd'].create(vals)
            if self.patient_id.email:
                templete_id = self.env.ref('cr_medical_base.mail_template_send_patient_review').id
                templete = self.env['mail.template'].browse(templete_id)
                templete.send_mail(self.id, force_send=True)

    @api.constrains("weekdays")
    def match_day_with_doctor(self):
        day_val = []
        for i in self:
            for day in i.doctor_id.weekly_avalibility_line:
                for week in day.available_weekdays:
                    day_val.append(week.name)

        if not day_val:
            raise ValidationError(_("Sorry,Doctor is not Available"))

    @api.constrains("appointment_date")
    def select_valid_date(self):
        today = date.today()
        if self.appointment_date < today:
            raise ValidationError('Please select valid date')

    @api.onchange("appointment_date")
    def select_weekday(self):
        if self.appointment_date:
            self.weekdays = self.appointment_date.strftime("%A")
            week_ids = self.env['weekday.name'].sudo().search([('name', '=', self.appointment_date.strftime("%A"))])
            return {'domain': {
                'select_time_id': [('available_weekdays', 'in', week_ids.ids), ('doctor_id', '=', self.doctor_id.id)]}}

    @api.model
    def create(self, values):
        if not values['weekdays']:
            day = values['appointment_date'].strftime("%A")
            values['weekdays'] = day
        self.create_new_patient()
        result = super(opdopd, self).create(values)
        if values['is_normal_opd'] == True:
            values['name'] = self.env['ir.sequence'].next_by_code('Appointment_seq')
        else:
            values['name'] = self.env['ir.sequence'].next_by_code('Appointment_follow_seq')

        result.name = values['name']
        for val in result:
            my_dict = {}
            for line in val.doctor_id.weekly_avalibility_line:
                time = line.name
                appointment = line.totel_appointment
                for week in line.available_weekdays:
                    if week.name in my_dict:
                        my_dict[week.name].append({str(time): str(appointment)})
                    if week.name not in my_dict:
                        my_dict.update({week.name: [{str(time): str(appointment)}]})
            weekdays = my_dict.get(str(val.weekdays))
            if weekdays:
                week_id = self.env['weekday.name'].sudo().search([('name', '=', val.weekdays)])
                tot_time = self.env["doctor.weeklyavalibility"].search(
                    [("available_weekdays", "in", week_id.ids), ("doctor_id", "=", val.doctor_id.id),
                     ("name", "=", val.select_time_id.name)])
                slot_dict = {}  # if doctor come twice in a day
                opd_record = self.env['opd.opd'].search_count(
                    [('weekdays', '=', str(val.weekdays)), ('doctor_id', '=', val.doctor_id.id),
                     ('select_time_id', '=', tot_time.id), ('appointment_date', '=', val.appointment_date)
                        , ('state', 'in', ['pending', 'confirm'])])

                for val in my_dict.get(val.weekdays):
                    for vals in val:
                        if vals == tot_time.name:
                            slot_ = val.get(tot_time.name)
                            slot_dict.update({'slot': slot_})
                if str(opd_record) >= str(slot_dict.get('slot')):
                    raise ValidationError("Appoint is Full")

        return result

    @api.onchange('existing_patient_name')
    def onchnage_existing_patient_name(self):
        if self.existing_patient_name:
            self.new_patient_name = ""
        else:
            self.patient_id = False

    @api.onchange('doctor_department_id')
    def onchange_opd_department_id(self):
        for rec in self:
            if rec.doctor_department_id:
                rec.doctor_id = False

    @api.onchange("appointment_date")
    def onchange_appointment(self):
        for rec in self:
            if rec.appointment_date:
                rec.select_time_id = False

    name = fields.Char("seq")
    opd_id = fields.Many2one('opd.opd', string="Opd")
    patient_id = fields.Many2one('res.partner', string='Patient', domain=[('is_patient', '=', True)])
    new_patient_id = fields.Many2one('res.partner', string='New Create Patient', domain=[('is_patient', '=', True)])
    existing_patient_name = fields.Boolean(string="Existing Patient")
    create_new_patient_button = fields.Boolean(default=False)
    new_patient_name = fields.Char(string="New Patient Name")
    doctor_department_id = fields.Many2one('doctor.department', string="Doctor Department", required=True)
    doctor_id = fields.Many2one('res.partner', string='Doctor', domain=[('is_doctor', '=', True)], required="True")
    appointment_date = fields.Date("Appointment Date", required="True")
    available_day = fields.Text()
    urgent_level = fields.Selection(
        [('normal', 'Normal'), ('urgent', 'Urgent'), ('medical_emergency', 'Medical Emergency')], string='Urgent Level')
    state = fields.Selection(
        [('draft', 'Draft'), ('pending', 'Pending'), ('confirm', 'Confirm'),
         ('sent', 'Done'), ('admitted', 'Admitted'), ('cancel', 'Cancel')], default='draft')
    weekdays = fields.Char("WeekDay Name")
    available_appointment_slot = fields.Char("Available Appointment Slot")
    select_time_id = fields.Many2one('doctor.weeklyavalibility', string='Select Time')
    medicine_line_ids = fields.One2many("pharmacy.prescription", 'opd_id')
    lab_line_ids = fields.One2many("laboratory.prescription", 'opd_id')
    radio_line_ids = fields.One2many("radiology.prescription", 'opd_id')
    symptoms_line_id = fields.One2many("symptoms.symptoms", 'opd_id')

    sex = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Sex')
    date_of_birth = fields.Date('Date of Birth', help='Date Of Birth')
    age = fields.Char('Age')
    blood_group = fields.Selection(
        [('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'),
         ('O-', 'O-')], 'Blood Group')
    email = fields.Char("Email", help='abc@gmail.com')
    mobile = fields.Char("Mobile", help='1234567890')
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    city = fields.Char("City")
    zip = fields.Char("Zip Code")
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    chief_complaints = fields.Many2one('chief.complaints', string="Chief Complaints")
    local_examination = fields.Many2one('local.examination', string="Local Examination")
    system_examination = fields.Many2one('system.examination', string="System Examination")

    pulse = fields.Char(string="Pulse")
    blood_pressure = fields.Char(string="BP")
    temp = fields.Char(string="Temperature")
    weight = fields.Char(string="Weight")
    respiration = fields.Char("Respiration")

    signed_by = fields.Binary(string='Signed By', attachment=True)
    is_new_patient = fields.Boolean('Is new patient')

    followup_advice = fields.Char(string="Followup Advice")
    follow_up_date = fields.Date(string="Followup Date")

    ipd_count = fields.Integer(string="IPD", compute="compute_count_ipd")
    laboratory_count = fields.Integer(string="Laboratory", compute="compute_laboratory_count")
    pharmacy_count = fields.Integer(string="Pharmacy", compute="compute_pharmacy_count")
    radiology_count = fields.Integer(string="Radiology", compute="compute_radiology_count")
    follow_up_opd_count = fields.Integer(string="Follow Up Opd", compute="compute_follow_up_opd_count")

    is_normal_opd = fields.Boolean(string="Normal Opd")
    is_follow_up_opd = fields.Boolean(string="Follow up Opd")
    ratings = ([('0', '0'),
                ('1', '1'),
                ('2', '2'),
                ('3', '3'),
                ('4', '4'),
                ('5', '5')])
    ratings = fields.Selection(ratings, string='Priority', index=True, default=ratings[0][0])
    feedback = fields.Text(string="Feedback")

    # =============================follow up opd count =====================
    def compute_follow_up_opd_count(self):
        for i in self:
            total_follow_up_opd = self.env['opd.opd'].search(
                [('opd_id', '=', self.id), ('is_follow_up_opd', '=', True)])
            i.follow_up_opd_count = len(total_follow_up_opd.ids)

    def patient_follow_up_opd_view(self):
        tree_view_id = self.env.ref('cr_medical_base.cr_follow_up_opd_patient_tree_view').id
        form_view_id = self.env.ref('cr_medical_base.cr_follow_up_opd_form_view').id

        return {'type': 'ir.actions.act_window',
                'name': _('Follow Up Opd History'),
                'res_model': 'opd.opd',
                'view_mode': 'tree,form',
                'res_id': False,
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'domain': [('opd_id', '=', self.id), ('is_follow_up_opd', '=', True)]
                }

    # =========================ipd count=============================
    def compute_count_ipd(self):
        for i in self:
            total_ipd = self.env['ipd.registration'].search(
                [('patient_id', '=', i.patient_id.id), ('ref_opd_id', '=', self.id)])
            i.ipd_count = len(total_ipd.ids)

    def patient_ipd_view(self):
        tree_view_id = self.env.ref('IPD.cr_ipd_registration_tree_view').id
        form_view_id = self.env.ref('IPD.cr_ipd_registration_form_view').id

        return {'type': 'ir.actions.act_window',
                'name': _('IPD History'),
                'res_model': 'ipd.registration',
                'view_mode': 'tree,form',
                'res_id': False,
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'domain': [('patient_id', '=', self.patient_id.id), ('ref_opd_id', '=', self.id)]
                }

    # ============================laboratory count=========================
    def compute_laboratory_count(self):
        for i in self:
            total_laboratory = self.env['laboratory.prescription'].search(
                [('patient_id', '=', i.patient_id.id), ('ref_opd_id', '=', self.id)])
            i.laboratory_count = len(total_laboratory.ids)

    def patient_laboratory_view(self):
        tree_view_id = self.env.ref('cr_medical_base.cr_laboratory_prescription_tree_view').id
        form_view_id = self.env.ref('cr_medical_base.cr_laboratory_prescription_form_view').id

        return {
            'name': 'laboratory History',
            'type': 'ir.actions.act_window',
            'res_model': 'laboratory.prescription',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('patient_id', '=', self.patient_id.id), ('ref_opd_id', '=', self.id)],
            'res_id': False,
            'target': 'current',
        }

    # ============================pharmacy count=========================

    def compute_pharmacy_count(self):
        for i in self:
            total_pharmacy = self.env['pharmacy.prescription'].search(
                [('patient_id', '=', i.patient_id.id), ('ref_opd_id', '=', self.id)])
            i.pharmacy_count = len(total_pharmacy.ids)

    def patient_pharmacy_view(self):
        tree_view_id = self.env.ref('cr_medical_base.cr_pharmacy_prescription_tree_view').id
        form_view_id = self.env.ref('cr_medical_base.cr_pharmacy_prescription_form_view').id

        return {
            'name': 'Pharmacy History',
            'type': 'ir.actions.act_window',
            'res_model': 'pharmacy.prescription',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('patient_id', '=', self.patient_id.id), ('ref_opd_id', '=', self.id)],
            'res_id': False,
            'target': 'current',
        }

    # ============================radiology count=========================

    def compute_radiology_count(self):
        for i in self:
            total_radiology = self.env['radiology.prescription'].search(
                [('patient_id', '=', i.patient_id.id), ('ref_opd_id', '=', self.id)])
            i.radiology_count = len(total_radiology.ids)

    def patient_radiology_view(self):
        tree_view_id = self.env.ref('cr_medical_base.cr_radiology_prescription_tree_view').id
        form_view_id = self.env.ref('cr_medical_base.cr_radiology_prescription_form_view').id

        return {
            'name': 'Radiology History',
            'type': 'ir.actions.act_window',
            'res_model': 'radiology.prescription',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('patient_id', '=', self.patient_id.id), ('ref_opd_id', '=', self.id)],
            'res_id': False,
            'target': 'current',
        }

    def send_email_message(self):
        today = fields.Date.today()
        opd_ids = self.search([('is_follow_up_opd', '=', True)])
        for opd in opd_ids:
            if opd.appointment_date:
                day = opd.appointment_date - today
                if str(day)[0].isnumeric() and int(str(day)[0]) == 1:
                    if opd.patient_id.email:
                        template_id = self.env.ref('cr_medical_base.mail_template_opd_opd').id
                        template = self.env['mail.template'].browse(template_id)
                        template.sudo().update({
                            'email_from': self.env.user.company_id.email,
                            'email_to': opd.patient_id.email
                        })
                        template.send_mail(opd.id, force_send=True)

                    if opd.patient_id.mobile:
                        username = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.username')
                        message = 'Dear ' + opd.patient_id.name + ',' + 'your next follow up opd on' + ' ' + str(
                            opd.appointment_date)
                        sendername = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.sendername')
                        smstype = "TRANS"
                        numbers = opd.patient_id.mobile
                        apikey = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.apikey')
                        URL = "http://sms.techofi.in/sendSMS?username=%s&message=%s&sendername=%s&smstype=%s&numbers=%s&apikey=%s" % (
                            username, message, sendername, smstype, numbers, apikey)

                        requests.get(url=URL)


class AvailableApppointment(models.Model):
    _name = "available.appointment"
    _description = "Show available slot of appointment"
    _rec_name = 'available_appointment_slot'

    weekdays = fields.Selection(
        [('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'),
         ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], string='Available Weekdays')
    available_appointment_slot = fields.Char("Available Appointment Slot")
    doctor_id = fields.Many2one("res.partner")
    state = fields.Selection([('draft', 'Draft'), ('booked', 'Booked')], default='draft')


class LocalExamination(models.Model):
    _name = "local.examination"
    _description = "local Examination"

    name = fields.Char()


class ChiefComplaints(models.Model):
    _name = "chief.complaints"
    _description = "Chief Complaints"

    name = fields.Char()


class SystemExamination(models.Model):
    _name = "system.examination"
    _description = "System Examination"

    name = fields.Char()


class IpdRegistration(models.Model):
    _name = "ipd.registration"
    _description = "Registering Inpatient Room"

    ref_opd_id = fields.Many2one('opd.opd')
    doctor_id = fields.Many2one('res.partner', string='Doctor', domain=[('is_doctor', '=', True)], required="True")
    doctor_department_id = fields.Many2one('doctor.department', string='Department')
    patient_id = fields.Many2one('res.partner', string='Patient', domain=[('is_patient', '=', True)])
    bed_id = fields.Many2one('bed.bed', string='Bed')


class Symptoms(models.Model):
    _name = "symptoms.symptoms"
    _description = "Symptoms symptoms"

    opd_id = fields.Many2one('opd.opd')
    symptoms_id = fields.Many2many('symptoms.type', string='Symptoms')
    symptoms_time_id = fields.Many2one('symptoms.time', 'Symptoms Time')


class SymptomsType(models.Model):
    _name = "symptoms.type"
    _description = "Symptoms Type"
    _rec_name = "type"

    type = fields.Char('name')


class SymptomsTime(models.Model):
    _name = "symptoms.time"
    _description = "Symptoms Time"
    _rec_name = "time"

    time = fields.Char('Time')


class InheritBed(models.Model):
    _name = "bed.bed"
    _description = "Bed bed"
