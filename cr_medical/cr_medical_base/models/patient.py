# -*- coding: utf-8 -*-
import random
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _


def random_token():
    chars = '0123456789'
    return ''.join(random.SystemRandom().choice(chars) for _ in range(8))


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def default_get(self, field_list):
        result = super(ResPartner, self).default_get(field_list)
        today_date = date.today()
        result.update({'enter_date': today_date})
        return result

    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth and record.is_patient:
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

    def pending(self):
        self.state = 'pending'

    def cancel(self):
        self.state = 'reject'

    def create_user(self):
        self.state = 'approve'

        for user in self:
            if not user.confirmation_ref:
                tokan = random_token()
                confirmation_ref = tokan + str(user.id)
                user.confirmation_ref = confirmation_ref
            values = {'partner_id': user.id,
                      'name': user.name,
                      'groups_id': self.env.ref('base.group_portal'),
                      'login': user.email,

                      }

            res = self.env['res.users'].sudo().create(values)
            self.user_id = res.id
            return res

    confirmation_ref = fields.Char("Confirmation Ref")
    sex = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Sex')
    age = fields.Char('Age', compute='_compute_age', store=True)
    blood_group = fields.Selection(
        [('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'),
         ('O-', 'O-')], 'Blood Group')
    date_of_birth = fields.Date('Date of Birth', help='Date Of Birth')
    marital_status = fields.Selection(
        [('single', 'Single'), ('married', 'Married'), ('widow', 'Widow'), ('divorced', 'Divorced')], 'Marital Status')
    is_patient = fields.Boolean('Is Patient')
    doctor_department_id = fields.Many2one('doctor.department', string="Doctor Department")
    doctor_id = fields.Many2one('res.partner', string="Doctor")
    user_id = fields.Many2one('res.users', string='User Id')
    enter_date = fields.Date(string="Date")

    pharmacy_count = fields.Integer("Pharmacy", compute="_compute_pharmacy_count", store=True)
    pharmacy_history_line_ids = fields.One2many('pharmacy.prescription', 'patient_id')

    laboratory_count = fields.Integer("Laboratory", compute="_compute_laboratory_count", store=True)
    laboratory_history_line_ids = fields.One2many('laboratory.prescription', 'patient_id')

    radiology_count = fields.Integer("Laboratory", compute="_compute_radiology_count", store=True)
    radiology_history_line_ids = fields.One2many('radiology.prescription', 'patient_id')

    opd_count = fields.Integer(compute="_compute_opd_count")

    state = fields.Selection(
        [('draft', 'Draft'), ("pending", "Pending"), ("approve", "Approved"), ("reject", "Rejected")],
        string="State", default="draft")

    def _compute_opd_count(self):
        for patient in self:
            patient.opd_count = self.env['opd.opd'].search_count(
                [('patient_id', '=', patient.id), ('is_normal_opd', '=', True)])

    @api.depends('laboratory_history_line_ids')
    def _compute_laboratory_count(self):
        for patient in self:
            patient.laboratory_count = len(patient.laboratory_history_line_ids.ids)

    @api.depends('radiology_history_line_ids')
    def _compute_radiology_count(self):
        for patient in self:
            patient.radiology_count = len(patient.radiology_history_line_ids.ids)

    @api.depends('pharmacy_history_line_ids')
    def _compute_pharmacy_count(self):
        for patient in self:
            patient.pharmacy_count = len(patient.pharmacy_history_line_ids.ids)

    @api.onchange('doctor_department_id')
    def onchange_department_id(self):
        for rec in self:
            if rec.doctor_department_id:
                rec.doctor_id = False

    def open_opd_view(self):
        form_view_id = self.env.ref('cr_medical_base.cr_opd_form_view').id
        tree_view_id = self.env.ref('cr_medical_base.cr_opd_tree_view').id
        return {
            'name': 'Appointment List',
            'type': 'ir.actions.act_window',
            'res_model': 'opd.opd',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_id': False,
            'target': 'current',
            'domain': [('patient_id', '=', self.id), ('is_normal_opd', '=', True)],
        }

    def open_pharmacy_view(self):
        tree_id = self.env.ref('cr_medical_base.cr_pharmacy_prescription_tree_view').id
        form_id = self.env.ref('cr_medical_base.cr_pharmacy_prescription_patient_form_view').id
        if self.pharmacy_count == 1:
            return {'type': 'ir.actions.act_window',
                    'name': _('Pharmacy History'),
                    'res_model': 'pharmacy.prescription',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': self.pharmacy_history_line_ids.id,
                    'views': [(form_id, 'form')],
                    'domain': [('patient_id', '=', self.id)]
                    }
        else:
            return {'type': 'ir.actions.act_window',
                    'name': _('Pharmacy History'),
                    'res_model': 'pharmacy.prescription',
                    'view_mode': 'tree,form',
                    'views': [(tree_id, 'tree'), (form_id, 'form')],
                    'domain': [('patient_id', '=', self.id)]}

    def open_laboratoray_view(self):
        tree_id = self.env.ref('cr_medical_base.cr_laboratory_prescription_tree_view').id
        form_id = self.env.ref('cr_medical_base.cr_laboratory_prescription_form_view').id

        if self.laboratory_count == 1:
            return {'type': 'ir.actions.act_window',
                    'name': _('Laboratory History'),
                    'res_model': 'laboratory.prescription',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': self.laboratory_history_line_ids.id,
                    'views': [(form_id, 'form')],
                    'domain': [('patient_id', '=', self.id)]
                    }
        else:
            return {'type': 'ir.actions.act_window',
                    'name': _('Laboratory History'),
                    'res_model': 'laboratory.prescription',
                    'view_mode': 'tree,form',
                    'views': [(tree_id, 'tree'), (form_id, 'form')],
                    'domain': [('patient_id', '=', self.id)]}

    def open_radiology_view(self):
        tree_id = self.env.ref('cr_medical_base.cr_radiology_prescription_tree_view').id
        form_id = self.env.ref('cr_medical_base.cr_radiology_prescription_form_view').id

        if self.radiology_count == 1:
            return {'type': 'ir.actions.act_window',
                    'name': _('Radiology History'),
                    'res_model': 'radiology.prescription',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': self.radiology_history_line_ids.id,
                    'views': [(form_id, 'form')],
                    'domain': [('patient_id', '=', self.id)]
                    }
        else:
            return {'type': 'ir.actions.act_window',
                    'name': _('Radiology History'),
                    'res_model': 'radiology.prescription',
                    'view_mode': 'tree,form',
                    'views': [(tree_id, 'tree'), (form_id, 'form')],
                    'domain': [('patient_id', '=', self.id)]}

    @api.model
    def create(self, vals_list):
        xml_patient_year_id = self.env.ref('cr_medical_base.patient_year_dashboard')
        xml_patient_month_id = self.env.ref('cr_medical_base.patient_month_dashboard')
        xml_patient_day_id = self.env.ref('cr_medical_base.patient_day_dashboard')
        res = super(ResPartner, self).create(vals_list)
        if res.is_patient:
            xml_patient_year_id.patient_ids = [(4, res.id)]
            xml_patient_month_id.patient_ids = [(4, res.id)]
            xml_patient_day_id.patient_ids = [(4, res.id)]
        return res
