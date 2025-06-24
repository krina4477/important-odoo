from collections import defaultdict

from odoo import fields, models


# from odoo.exceptions import ValidationError


class Surgeryeport(models.TransientModel):
    _name = "surgery.report"
    _description = "Surgery report"

    def _get_years(self):
        return [(i, str(i)) for i in range(fields.Date.today().year, 1995, -1)]

    name = fields.Char('Name', default='IPD Report')
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    select_report = (fields.Selection(
        [('group_by_department_surgery', 'Department Wise Report'),
         ('group_by_doctor_surgery', 'Doctor Wise Report'), ('group_by_diseases', 'Diseases Wise Report')]))
    department_ids = fields.Many2many('doctor.department', string='Department')
    doctor_ids = fields.Many2many('res.partner', string='Doctor')
    # , domain = [('is_doctor', '=', True)]
    select_years = fields.Selection(selection=_get_years)

    def button_export_pdf(self):
        user_date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
        domain = [('surgery_date', '>=', self.start_date), ('surgery_date', '<=', self.end_date)]
        ipd_id = self.env['show.ipd.surgery'].sudo().search(domain)

        # ------------------------------------department wise surgery report-----------------------------------------------.

        if self.start_date and self.end_date and self.select_report == 'group_by_department_surgery':
            departments_dict = defaultdict(list)  # Use defaultdict to group surgery records by department
            if self.department_ids:
                domain += [('doctor_id.doctor_department_id', 'in', self.department_ids.ids)]
                dep_ipd_id = self.env['show.ipd.surgery'].search(domain)
            else:
                dep_ipd_id = ipd_id
            for rec in dep_ipd_id:
                if rec.doctor_id.doctor_department_id.department:
                    departments_dict[rec.doctor_id.doctor_department_id.department].append(rec.id)

            # Pass the grouped data to the report template
            data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'record': departments_dict
            }
            return self.env.ref('surgery.action_surgery_department_reports').report_action(self, data=data)

        # --------------------------------surgery report doctor wise -------------------------------------

        if self.start_date and self.end_date and self.select_report == 'group_by_doctor_surgery':
            doctors_dict = defaultdict(list)  # Use defaultdict to group surgery records by department
            if self.doctor_ids:
                # selected_doctor_ids = self.doctor_ids.ids
                domain += [('doctor_id.id', 'in', self.doctor_ids.ids)]
                dep_ipd_id = self.env['show.ipd.surgery'].search(domain)
            else:
                dep_ipd_id = ipd_id
            for rec in dep_ipd_id:
                if rec.doctor_id.id and rec.doctor_id.name:
                    doctors_dict[rec.doctor_id.name].append(rec.id)

            # Pass the grouped data to the report template
            data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'record': doctors_dict
            }
            return self.env.ref('surgery.action_surgery_doctor_reports').report_action(self, data=data)

        # ----------------------------------------surgery diseases wise report------------------------------------
        if self.start_date and self.end_date and self.select_report == 'group_by_diseases':
            ipd_list = []
            for ipd in ipd_id:
                age = ipd.ipd_id.patient_id.age
                vals = {
                    'name': ipd.ipd_id.name,
                    'patient_name': ipd.patient_id.name,
                    'surgery_id': ipd.surgery_id.display_name,
                    'age': age,
                    'sex': ipd.ipd_id.patient_id.sex,
                    'doctor_department_id': ipd.ipd_id.doctor_department_id.department,
                    'doctor_id': ipd.doctor_id.name,
                    'date_of_admit': ipd.ipd_id.date_of_admit,
                    'surgery_date': ipd.surgery_date,
                }
                ipd_list.append(vals)
            data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'search_record': ipd_list
            }
            return self.env.ref('surgery.action_surgery_diseases_reports').report_action(self, data=data)

        # --------------------------------surgery report (start_date end_date range)----------------------------
        if self.start_date and self.end_date:
            user_date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
            ipd_list = []
            for ipd in ipd_id:
                vals = {
                    'name': ipd.ipd_id.name,
                    'patient_name': ipd.patient_id.name,
                    'surgery_date': ipd.surgery_date,
                    'doctor_department_id': ipd.ipd_id.doctor_department_id.department,
                    'doctor_id': ipd.doctor_id.name,
                    'date_of_admit': ipd.ipd_id.date_of_admit,
                    'surgery_id': ipd.surgery_id.display_name,
                    'state': ipd.state,
                    'start_time': ipd.start_time,
                    'end_time': ipd.end_time,
                    'doctor_remark': ipd.doctor_remark,
                    'ot_remark': ipd.ot_remark,
                    'action': ipd.action,
                }
                ipd_list.append(vals)
            data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'search_record': ipd_list
            }
            return self.env.ref('surgery.action_surgery_reports').report_action(self, data=data)
