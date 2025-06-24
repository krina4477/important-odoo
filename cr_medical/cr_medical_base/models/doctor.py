# -*- coding: utf-8 -*-
from datetime import date

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def doctor_open_pharmacy_view(self):
        tree_id = self.env.ref('cr_medical_base.cr_pharmacy_prescription_tree_view').id
        form_id = self.env.ref('cr_medical_base.cr_pharmacy_prescription_patient_form_view').id
        return {'type': 'ir.actions.act_window',
                'name': _('Pharmacy History'),
                'res_model': 'pharmacy.prescription',
                'view_mode': 'tree,form',
                'views': [(tree_id, 'tree'), (form_id, 'form')],
                'domain': [('doctor_id', '=', self.id)]}

    def doctor_open_laboratory_view(self):
        tree_id = self.env.ref('cr_medical_base.cr_laboratory_prescription_tree_view').id
        form_id = self.env.ref('cr_medical_base.cr_laboratory_prescription_form_view').id
        return {'type': 'ir.actions.act_window',
                'name': _('Laboratory History'),
                'res_model': 'laboratory.prescription',
                'view_mode': 'tree,form',
                'views': [(tree_id, 'tree'), (form_id, 'form')],
                'domain': [('doctor_id', '=', self.id)]}

    def doctor_open_ipd_view(self):
        tree_id = self.env.ref('IPD.cr_ipd_registration_tree_view').id
        form_id = self.env.ref('IPD.cr_ipd_registration_form_view').id
        return {'type': 'ir.actions.act_window',
                'name': _('IPD History'),
                'res_model': 'ipd.registration',
                'view_mode': 'tree,form',
                'views': [(tree_id, 'tree'), (form_id, 'form')],
                'domain': [('doctor_id', '=', self.id)]}

    def doctor_open_radiology_view(self):
        tree_id = self.env.ref('cr_medical_base.cr_radiology_prescription_tree_view').id
        form_id = self.env.ref('cr_medical_base.cr_radiology_prescription_form_view').id
        return {'type': 'ir.actions.act_window',
                'name': _('Radiology History'),
                'res_model': 'radiology.prescription',
                'view_mode': 'tree,form',
                'views': [(tree_id, 'tree'), (form_id, 'form')],
                'domain': [('doctor_id', '=', self.id)]}

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        xml_doctor_id = self.env.ref('cr_medical_base.doctor_dashboard').id
        if res.is_doctor:
            res.doctor_dashboard_id = xml_doctor_id
        return res

    # @api.multi
    def toggle_appointment_active(self):
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
            'domain': [('doctor_id', '=', self.id), ('is_normal_opd', '=', True)],
        }

    def compute_count(self):
        for appointment in self:
            appointment.appointment_count = self.env["opd.opd"].sudo().search_count(
                [('doctor_id', '=', appointment.id), ('is_normal_opd', '=', True)])

    @api.constrains("joining_date")
    def select_valid_date(self):
        if self.joining_date:
            today = date.today()
            if self.joining_date > today:
                raise ValidationError('Please select valid date')

    # Start DeshBoard

    def _get_action(self, action_xmlid):
        # TDE TODO check to have one view + custo in methods
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['domain'] = [('doctor_id', '=', self.id)]
        return action

    def get_doctor_detail(self):
        return self._get_action('cr_medical_base.action_appointment_new_listing_details')

    def _get_confirm_action(self, action_xmlid):
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['domain'] = [('doctor_id', '=', self.id), ('state', 'in', ['confirm', 'sent', 'done'])]
        return action

    # @api.one
    def compute_count_confirm(self):
        for i in self:
            a = self.env["opd.opd"].search([('state', 'in', ['confirm', 'sent', 'done']), ('doctor_id', '=', i.id)])
            i.confirm_count = len(a.ids)

    def get_state_confirm_details(self):
        return self._get_confirm_action('cr_medical_base.action_cr_opd_patient_information')

    def _get_pending_action(self, action_xmlid):
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['domain'] = [('doctor_id', '=', self.id), ('state', '=', 'pending')]
        return action

    # @api.one
    def compute_count_pending(self):
        for i in self:
            a = self.env["opd.opd"].search([('state', '=', 'pending'), ('doctor_id', '=', i.id)])
            i.pending_count = len(a.ids)

    def get_state_pending_details(self):
        return self._get_pending_action('cr_medical_base.action_cr_opd_patient_information')

    def _get_cancel_action(self, action_xmlid):
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['domain'] = [('doctor_id', '=', self.id), ('state', '=', 'cancel')]
        return action

    # @api.one
    def compute_count_cancel(self):
        for i in self:
            a = self.env["opd.opd"].search([('state', '=', 'cancel'), ('doctor_id', '=', i.id)])
            i.cancel_count = len(a.ids)

    def get_state_cancel_details(self):
        return self._get_cancel_action('cr_medical_base.action_cr_opd_patient_information')

    ####END DeshBoard

    def pending(self):
        self.state = 'pending'

    def cancel(self):
        self.state = 'reject'

    def create_user_1(self):
        self.state = 'approve'
        for user in self:
            values = {'partner_id': user.id,
                      'name': user.name,
                      'login': user.email,
                      # 'groups_id': [(6, 0, [self.env.ref('cr_medical_base.group_doctor').id,
                      #                       self.env.ref('base.group_user').id])],
                      'groups_id': self.env.ref('base.group_portal'),
                      'state': 'active',
                      }
            result = self.env['res.users'].create(values)
            # result.sudo().action_reset_password()
            self.user_id = result.id
            return result

    sex = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Sex')
    speciality_ids = fields.Many2many('doctor.speciality', string='Speciality')
    degree_ids = fields.Many2many('doctor.degree', string='Degree')
    doctor_department_id = fields.Many2one('doctor.department', string='Department')
    doctor_fees = fields.Char('Fees')
    doctor_dashboard_id = fields.Many2one('dashboard')
    registration_no = fields.Char('Registration No')
    working_institute = fields.Char('Working Institute')
    work_location = fields.Char('Work Location')
    weekly_avalibility_line = fields.One2many("doctor.weeklyavalibility", "doctor_id", 'Doctor Availablity')
    dr_form_no = fields.Char("Doctor Form Number")
    bool_field = fields.Boolean("Confirm", default=False)
    appointment_count = fields.Integer(compute="compute_count")
    joining_date = fields.Date(string="Doctor Joining Date")
    is_doctor = fields.Boolean('Is Doctor')
    patient_id = fields.Many2one("opd.opd", string="Patient Name")
    user_id = fields.Many2one('res.users', string='User Id')
    confirm_count = fields.Char(compute="compute_count_confirm")
    pending_count = fields.Char(compute="compute_count_pending")
    doctor_description = fields.Text(string='Description')
    cancel_count = fields.Char(compute="compute_count_cancel")
    sign_by = fields.Binary('Signature')
    total_experience = fields.Char('Total Experience')
    about_doctor = fields.Text('About')
    licence = fields.Char("License Id")
    # color = fields.Integer('Color Index', compute="change_colore_on_kanban")
    state = fields.Selection(
        [('draft', 'Draft'), ("pending", "Pending"), ("approve", "Approved"), ("reject", "Rejected")],
        string="State", default="draft")
    doc_language = fields.Many2many("res.lang", string="language")
    doctor_pharmacy_count = fields.Integer("Pharmacy", compute="_compute_doctor_count")
    doctor_laboratory_count = fields.Integer("Laboratory", compute="_compute_doctor_count")
    doctor_radiology_count = fields.Integer("Radiology", compute="_compute_doctor_count")
    doctor_ipd_count = fields.Integer("IPDs", compute="_compute_doctor_count")

    def _compute_doctor_count(self):
        for doctor in self:
            doctor.doctor_pharmacy_count = self.env['pharmacy.prescription'].sudo().search_count(
                [('doctor_id', '=', doctor.id)])
            doctor.doctor_laboratory_count = self.env['laboratory.prescription'].sudo().search_count(
                [('doctor_id', '=', doctor.id)])
            doctor.doctor_radiology_count = self.env['radiology.prescription'].sudo().search_count(
                [('doctor_id', '=', doctor.id)])
            doctor.doctor_ipd_count = self.env['ipd.registration'].sudo().search_count(
                [('doctor_id', '=', doctor.id)])


class weeklyavalibility(models.Model):
    _name = "doctor.weeklyavalibility"
    _description = "Doctor Weekly Schedule"

    @api.onchange('from_time', 'to_time')
    def totall_time(self):
        for i in self:
            if i.from_time and i.to_time:
                i.name = str(i.from_time.name) + ' To ' + str(i.to_time.name)

    available_weekdays = fields.Many2many('weekday.name', string='Available Weekdays')
    from_time = fields.Many2one('time.hours', string='From Time (24hr)')
    to_time = fields.Many2one('time.hours', string='To Time (24hr)')

    totel_appointment = fields.Integer("Total Appointment")
    name = fields.Char(string='Total Time')
    doctor_id = fields.Many2one("res.partner")


class TimeHours(models.Model):
    _name = "time.hours"
    _description = "Time Hours"
    # _rec_name = "time"

    name = fields.Char('Name', required="True")
    time = fields.Float('Time', required="True")


class Week_Name(models.Model):
    _name = "weekday.name"
    _description = "Week Name"

    name = fields.Char("WeekDay")


class speciality(models.Model):
    _name = "doctor.speciality"
    _description = "Doctor Speciality"
    _rec_name = "speciality"

    speciality = fields.Char("Speciality")


class degree(models.Model):
    _name = "doctor.degree"
    _description = "Doctor Degree"
    _rec_name = "degree"

    degree = fields.Char("Degree")


class Department(models.Model):
    _name = "doctor.department"
    _description = "Doctor Department"
    _rec_name = "department"

    department = fields.Char("Department")
    department_dashboard_id = fields.Many2one('dashboard')

    @api.model
    def create(self, vals_list):
        xml_department_id = self.env.ref('cr_medical_base.department_dashboard').id
        vals_list['department_dashboard_id'] = xml_department_id
        return super(Department, self).create(vals_list)
