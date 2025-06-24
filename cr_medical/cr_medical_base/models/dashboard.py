# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import datetime


class Dashboard(models.Model):
    _name = "dashboard"
    _description = "Dashboard"

    name = fields.Char()
    patient_ids = fields.Many2many('res.partner')
    doctor_ids = fields.One2many('res.partner', 'doctor_dashboard_id')
    department_ids = fields.One2many('doctor.department', 'department_dashboard_id')
    count_patient = fields.Integer("Total Patients of this Year", compute="_compute_patient")
    color = fields.Integer('Color Index')
    color2 = fields.Char()
    admit_patient_ids = fields.Many2one('ipd.registration')

    @api.depends('patient_ids', 'doctor_ids', 'department_ids', 'admit_patient_ids')
    def _compute_patient(self):
        for dashboard in self:
            now_date = datetime.date.today()
            total_year = 0.0
            total_month = 0.0
            total_day = 0.0

            for patient in dashboard.patient_ids:
                if patient.enter_date and patient.enter_date.year == now_date.year:
                    total_year += 1
                if patient.enter_date and patient.enter_date.month == now_date.month:
                    total_month += 1
                if patient.enter_date and patient.enter_date == now_date:
                    total_day += 1

            xml_patient_year_id = self.env.ref('cr_medical_base.patient_year_dashboard').id
            xml_patient_month_id = self.env.ref('cr_medical_base.patient_month_dashboard').id
            xml_patient_day_id = self.env.ref('cr_medical_base.patient_day_dashboard').id
            xml_doctor_id = self.env.ref('cr_medical_base.doctor_dashboard').id
            xml_department_id = self.env.ref('cr_medical_base.department_dashboard').id
            xml_admit_patient_id = self.env.ref('cr_medical_base.admit_patient_dashboard').id

            admit_patient_list = self.env['ipd.registration'].sudo().search([])

            if dashboard.id == xml_patient_year_id:
                dashboard.count_patient = total_year

            elif dashboard.id == xml_patient_month_id:

                dashboard.count_patient = total_month

            elif dashboard.id == xml_patient_day_id:
                dashboard.count_patient = total_day

            elif dashboard.id == xml_doctor_id:
                dashboard.count_patient = len(dashboard.doctor_ids.ids)

            elif dashboard.id == xml_department_id:
                dashboard.count_patient = len(dashboard.department_ids.ids)

            elif dashboard.id == xml_admit_patient_id:
                dashboard.count_patient = len(admit_patient_list)
            else:
                dashboard.count_patient = 0.0

    def get_records(self):
        patient_tree_id = self.env.ref('cr_medical_base.cr_patient_tree_view').id
        patient_form_id = self.env.ref('cr_medical_base.cr_patient_form_view').id

        # ============================= Year Patient List ====================================
        xml_patient_year_id = self.env.ref('cr_medical_base.patient_year_dashboard').id
        if self.id == xml_patient_year_id:
            now_date = datetime.date.today()
            patient_list = []
            for patient in self.patient_ids:
                if patient.enter_date and patient.enter_date.year == now_date.year:
                    patient_list.append(patient.id)

            return {
                'type': 'ir.actions.act_window',
                'name': _('Patient'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'res.partner',
                'views': [(patient_tree_id, 'tree'), (patient_form_id, 'form')],
                'domain': [('id', 'in', patient_list)]
            }

        # =========================== Month Patient List ======================================
        xml_patient_month_id = self.env.ref('cr_medical_base.patient_month_dashboard').id
        if self.id == xml_patient_month_id:
            now_date = datetime.date.today()
            patient_list = []
            for patient in self.patient_ids:
                if patient.enter_date and patient.enter_date.month == now_date.month:
                    patient_list.append(patient.id)

            return {
                'type': 'ir.actions.act_window',
                'name': _('Patient'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'res.partner',
                'views': [(patient_tree_id, 'tree'), (patient_form_id, 'form')],
                'domain': [('id', 'in', patient_list)]
            }

        # ========================== Day Patient List ======================================
        xml_patient_day_id = self.env.ref('cr_medical_base.patient_day_dashboard').id
        if self.id == xml_patient_day_id:
            now_date = datetime.date.today()
            patient_list = []
            for patient in self.patient_ids:
                if patient.enter_date and patient.enter_date == now_date:
                    patient_list.append(patient.id)

            return {
                'type': 'ir.actions.act_window',
                'name': _('Patient'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'res.partner',
                'views': [(patient_tree_id, 'tree'), (patient_form_id, 'form')],
                'domain': [('id', 'in', patient_list)]
            }

        # ================================== Doctor List ==============================
        xml_doctor_id = self.env.ref('cr_medical_base.doctor_dashboard').id
        if self.id == xml_doctor_id:
            doctor_tree_id = self.env.ref('cr_medical_base.cr_doctor_tree_view').id
            docotr_form_id = self.env.ref('cr_medical_base.cr_doctor_form_view').id
            return {
                'type': 'ir.actions.act_window',
                'name': _('Doctor'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'res.partner',
                'views': [(doctor_tree_id, 'tree'), (docotr_form_id, 'form')],
                'domain': [('id', 'in', self.doctor_ids.ids), ('is_doctor', '=', True)]
            }

        # =========================== Department List =============================
        xml_department_id = self.env.ref('cr_medical_base.department_dashboard').id
        if self.id == xml_department_id:
            department_tree_id = self.env.ref('cr_medical_base.cr_doctor_department_tree_view').id
            return {
                'type': 'ir.actions.act_window',
                'name': _('Department'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'doctor.department',
                'views': [(department_tree_id, 'tree')],
                'domain': [('id', 'in', self.department_ids.ids)]
            }

        # ============================= admit_patient List ================================
        xml_admit_patient_id = self.env.ref('cr_medical_base.admit_patient_dashboard').id
        if self.id == xml_admit_patient_id:
            now_date = datetime.date.today()
            admit_patient_tree_id = self.env.ref('IPD.cr_ipd_registration_tree_view').id
            admit_patient_form_id = self.env.ref('IPD.cr_ipd_registration_form_view').id
            admit_patient_ids = self.env['ipd.registration'].sudo().search([])
            admit_patient_list = []
            for rec in admit_patient_ids:
                if rec.date_of_admit:
                    if rec.date_of_admit.year == now_date.year:
                        admit_patient_list.append(rec.id)
            return {
                'type': 'ir.actions.act_window',
                'name': _('Admit Patient'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'ipd.registration',
                'views': [(admit_patient_tree_id, 'tree'), (admit_patient_form_id, 'form')],
                'domain': [('id', 'in', admit_patient_list)]
            }
