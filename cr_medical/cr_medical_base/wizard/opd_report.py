from odoo import fields, models, api, _
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ReportWizard(models.TransientModel):
    _name = "opd.reports"
    _description = "Opd reports"

    def _get_years(self):
        return [(i, str(i)) for i in range(fields.Date.today().year, 1995, -1)]

    name = fields.Char('Name', default='Opd Report')
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    select_report = fields.Selection([
        ('group_by_department_opd', 'Department Wise Opd'),
        ('group_by_month_opd', 'Month Wise Opd'),
        ('group_by_medicine_patient', 'Medicine Wise Opd'),
        ('group_by_medicine_department', 'Department Wise Medicine'), ])
    # group_by_department_opd = fields.Boolean('Select Department')
    department_ids = fields.Many2many('doctor.department', string='Department')
    # group_by_month_opd = fields.Boolean(string='Month')
    select_years = fields.Selection(selection=_get_years)
    # group_by_medicine_patient = fields.Boolean("Medicine report Patient Wise")
    # group_by_medicine_department = fields.Boolean("Medicine report Department Wise")
    patient_count = fields.Boolean("Report Patient Count")

    def button_export_pdf(self):
        user_date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
        domain = [('appointment_date', '>=', self.start_date),
                  ('appointment_date', '<=', self.end_date)]
        opd_id = self.env['opd.opd'].sudo().search(domain)

        # ----------------------------------opd patient count report male and female wise----------------------------------
        if self.patient_count and self.start_date and self.end_date:
            domain += [('state', '=', 'sent')]
            dis_opd_id = self.env['opd.opd'].sudo().search(domain)

            admission_dict = {}
            for rec in opd_id:
                if rec.doctor_department_id.department in admission_dict:
                    if rec.patient_id.sex == 'male' or rec.new_patient_id.sex == 'male':
                        admission_dict[rec.doctor_department_id.department].update(
                            {'male': int(admission_dict[rec.doctor_department_id.department].get('male')) + 1, })
                    if rec.patient_id.sex == 'female' or rec.new_patient_id.sex == 'female':
                        admission_dict[rec.doctor_department_id.department].update(
                            {'female': int(admission_dict[rec.doctor_department_id.department].get('female')) + 1})
                else:
                    if rec.patient_id.sex == 'male' or rec.new_patient_id.sex == 'male':
                        admission_dict[rec.doctor_department_id.department] = {'male': 1, 'female': 0,
                                                                               'dis_male': 0,
                                                                               'dis_female': 0}
                    if rec.patient_id.sex == 'female' or rec.new_patient_id.sex == 'female':
                        admission_dict[rec.doctor_department_id.department] = {'male': 0, 'female': 1, 'dis_male': 0,
                                                                               'dis_female': 0}

            for rec in dis_opd_id:
                if rec.doctor_department_id.department in admission_dict:
                    if rec.patient_id.sex == 'male':
                        admission_dict[rec.doctor_department_id.department].update(
                            {'dis_male': int(
                                admission_dict[rec.doctor_department_id.department].get('dis_male')) + 1, })
                    if rec.patient_id.sex == 'female':
                        admission_dict[rec.doctor_department_id.department].update(
                            {'dis_female': int(
                                admission_dict[rec.doctor_department_id.department].get('dis_female')) + 1})
            data = {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'search_record': admission_dict,
            }
            return self.env.ref('cr_medical_base.action_patient_count_reports').report_action(self, data=data)

        # ------------------------ medicine report department wise--------------------------------------

        if self.select_report == 'group_by_medicine_department' and self.start_date and self.end_date:
            opd_vals = []
            for opd in opd_id:
                for op in opd.medicine_line_ids:
                    for med in op.medicine_id:
                        opd_vals.append({
                            'medicine_id': med.name,
                            'department': opd.doctor_department_id.department,
                            'total_tablets': op.total_tablets
                        })
            unique_medicines = {}
            for item in opd_vals:
                key = (item['medicine_id'], item['department'])
                if key in unique_medicines:
                    unique_medicines[key]['total_tablets'] += item['total_tablets']
                else:
                    unique_medicines[key] = item

            # Convert the dictionary values back to a list
            result = list(unique_medicines.values())
            data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'search_record': result
            }
            return self.env.ref('cr_medical_base.action_medicine_department_reports').report_action(self,
                                                                                                    data=data)

        # --------------------------Medicine Report Patient Wise----------------------------
        if self.start_date and self.end_date and self.select_report == 'group_by_medicine_patient':
            opd_list = []
            for opd in opd_id:
                medicine_list = []
                for med in opd.medicine_line_ids:
                    for res in med.medicine_id:
                        medicine_list.append(res.name)
                vals = {
                    'name': opd.name,
                    'patient_id': opd.patient_id.name,
                    'new_patient_name': opd.new_patient_name,
                    'doctor_department_id': opd.doctor_department_id.department,
                    'doctor_id': opd.doctor_id.name,
                    'medicine': medicine_list,
                    'appointment_date': opd.appointment_date,
                    'weekdays': opd.weekdays,
                }
                opd_list.append(vals)
            data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'search_record': opd_list
            }
            return self.env.ref('cr_medical_base.action_opd_medicine_patient_reports').report_action(self,
                                                                                                     data=data)

            # --------------------------------------Opd Report Department Wise------------------------------------
        if self.start_date and self.end_date and self.select_report == 'group_by_department_opd':
            departments_dict = {}
            if self.department_ids:
                domain += [('doctor_department_id', 'in', self.department_ids.ids)]
                dep_opd_id = self.env['opd.opd'].search(domain)
            else:
                dep_opd_id = opd_id
            for rec in dep_opd_id:
                if rec.doctor_department_id.department in departments_dict:
                    departments_dict[rec.doctor_department_id.department].append(rec.id)
                else:
                    departments_dict[rec.doctor_department_id.department] = [rec.id]
            data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'record': departments_dict
            }
            return self.env.ref('cr_medical_base.action_opd_department_reports').report_action(self, data=data)

        # --------------------------opd report month wise--------------------------------
        if self.select_report == 'group_by_month_opd':
            department_dict = {}
            selected_year = self.select_years
            opd_ids = self.env['opd.opd'].search(
                [('is_normal_opd', '=', True)])
            year_opds = opd_ids.filtered(lambda op: op.appointment_date.year == int(selected_year))
            if year_opds:
                for opd in year_opds:
                    if opd.doctor_department_id.department in department_dict:
                        if department_dict[opd.doctor_department_id.department].get(
                                opd.appointment_date.strftime('%B'),
                                False):
                            old_value = department_dict[opd.doctor_department_id.department].get(
                                opd.appointment_date.strftime('%B'), False)
                            department_dict[opd.doctor_department_id.department][
                                opd.appointment_date.strftime('%B')] = old_value + 1
                        else:
                            department_dict[opd.doctor_department_id.department][
                                opd.appointment_date.strftime('%B')] = 1
                    else:
                        department_dict[opd.doctor_department_id.department] = {
                            opd.appointment_date.strftime('%B'): 1}
                data = {
                    'select_years': self.select_years,
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'record': department_dict,
                }
                return self.env.ref('cr_medical_base.action_opd_month_reports').report_action(self, data=data)
            else:
                raise ValidationError("Record not found of this year")
        #     ------------------------------opd report start date end date -----------------------------------
        if self.start_date and self.end_date:
            user_date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
            opd_list = []
            for opd in opd_id:
                vals = {
                    'name': opd.name,
                    'patient_id': opd.patient_id.name,
                    'new_patient_name': opd.new_patient_name,
                    'age': opd.patient_id.age.split(',')[0] if opd.patient_id.age else False,
                    'new_patient_age': opd.new_patient_id.age.split(',')[0] if opd.new_patient_id.age else False,
                    'sex': opd.patient_id.sex,
                    'new_patient_sex': opd.new_patient_id.sex,
                    'doctor_department_id': opd.doctor_department_id.department,
                    'doctor_id': opd.doctor_id.name,
                    'appointment_date': opd.appointment_date,
                    'select_time_id': opd.select_time_id.name,
                    'weekdays': opd.weekdays,
                }
                opd_list.append(vals)
            data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'search_record': opd_list
            }
            return self.env.ref('cr_medical_base.action_opd_reports').report_action(self, data=data)
