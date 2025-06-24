from odoo import fields, models
from odoo.exceptions import ValidationError


class IpdReports(models.TransientModel):
    _name = "ipd.reports"
    _description = "Ipd reports"

    def _get_years(self):
        return [(i, str(i)) for i in range(fields.Date.today().year, 1995, -1)]

    name = fields.Char('Name', default='IPD Report')
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    select_report = fields.Selection(
        [('group_by_department_ipd', 'Department Wise Ipd'), ('group_by_month_ipd', 'Month Wise IPD'),
         ('group_by_medicine_patient', 'Medicine Wise IPD'),
         ('group_by_medicine_department', 'Department Wise Medicine'), ('patient_count', 'Patient Count'),
         ('ipd_bed_count', 'Ipd Bed Count'), ('discharge_summary', 'Discharge Summary')])
    department_ids = fields.Many2many('doctor.department', string='Department')
    select_years = fields.Selection(selection=_get_years)

    def button_export_pdf(self):
        user_date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
        domain = [('date_of_admit', '>=', self.start_date), ('date_of_admit', '<=', self.end_date)]
        ipd_id = self.env['ipd.registration'].sudo().search(domain)

        # --------------------------------ipd bed count report-------------------------------
        if self.select_report == 'ipd_bed_count' and self.start_date and self.end_date:
            bed_count_dict = {}
            for rec in ipd_id:
                # create dict department wise male and female
                if rec.doctor_department_id.department in bed_count_dict:
                    if rec.state != 'discharge':
                        if rec.patient_id.sex == 'male':
                            bed_count_dict[rec.doctor_department_id.department].update(
                                {'male': int(bed_count_dict[rec.doctor_department_id.department].get('male')) + 1, })
                        if rec.patient_id.sex == 'female':
                            bed_count_dict[rec.doctor_department_id.department].update(
                                {'female': int(bed_count_dict[rec.doctor_department_id.department].get('female')) + 1})
                else:
                    if rec.state != 'discharge':
                        if rec.patient_id.sex == 'male':
                            bed_count_dict[rec.doctor_department_id.department] = {'male': 1, 'female': 0}
                        if rec.patient_id.sex == 'female':
                            bed_count_dict[rec.doctor_department_id.department] = {'male': 0, 'female': 1}
                    else:
                        bed_count_dict[rec.doctor_department_id.department] = {'male': 0, 'female': 0}
            bed_count_data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'bed_count_dict': bed_count_dict
            }
            return self.env.ref('IPD.action_ipd_bed_count_reports').report_action(self, data=bed_count_data)

        # -----------------------------------ipd discharge summary report-----------------------------------
        if self.select_report == 'discharge_summary' and self.start_date and self.end_date:
            domain += [('state', '=', 'discharge')]
            ipd_search = self.env['ipd.registration'].sudo().search(domain)
            departments_dict = {}
            if self.department_ids:
                domain += [('doctor_department_id', 'in', self.department_ids.ids)]
                dep_opd_id = self.env['ipd.registration'].search(domain)
            else:
                dep_opd_id = ipd_search
            for rec in dep_opd_id:
                # create dict department wise discharge patient id
                if rec.doctor_department_id.department in departments_dict:
                    departments_dict[rec.doctor_department_id.department].append(rec.id)
                else:
                    departments_dict[rec.doctor_department_id.department] = [rec.id]
            data_dict = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'record': departments_dict
            }
            return self.env.ref('IPD.action_ipd_discharge_summary_reports').report_action(self, data=data_dict)

        # ----------------------------------- ipd department wise medicines report-----------------------------.
        if self.select_report == 'group_by_medicine_department' and self.start_date and self.end_date:
            user_date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
            ipd_vals = []
            for ipd in ipd_id:
                for ip in ipd.ipd_summary_line_ids:
                    ipd_vals.append({
                        'medicine_id': ip.medicine_detail.name,
                        'department': ipd.doctor_department_id.department,
                        'total_tablets': ip.total_tablets
                    })
            unique_medicines = {}
            # create dict department wise medicine
            for item in ipd_vals:
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
            return self.env.ref('IPD.action_ipd_medicine_department_reports').report_action(self, data=data)

        # ------------------------------------department wise ipd report-----------------------------------------------.
        if self.start_date and self.end_date and self.select_report == 'group_by_department_ipd':
            departments_dict = {}
            if self.department_ids:
                domain += [('doctor_department_id', 'in', self.department_ids.ids)]
                dep_ipd_id = self.env['ipd.registration'].search(domain)
            else:
                dep_ipd_id = ipd_id
            for rec in dep_ipd_id:
                if rec.doctor_department_id.department in departments_dict:
                    departments_dict[rec.doctor_department_id.department].append(rec.id)
                else:
                    departments_dict[rec.doctor_department_id.department] = [rec.id]
            data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'record': departments_dict
            }
            return self.env.ref('IPD.action_ipd_department_reports').report_action(self, data=data)

        # -------------------------------------month wise ipd reort.--------------------------------
        if self.select_report == 'group_by_month_ipd':
            department_dict = {}
            selected_year = self.select_years
            ipd_ids = self.env['ipd.registration'].search([])
            year_ipds = ipd_ids.filtered(lambda ip: ip.date_of_admit.year == int(selected_year))
            if year_ipds:
                for ipd in year_ipds:
                    if ipd.doctor_department_id.department in department_dict:
                        if department_dict[ipd.doctor_department_id.department].get(ipd.date_of_admit.strftime('%B'),
                                                                                    False):
                            old_value = department_dict[ipd.doctor_department_id.department].get(
                                ipd.date_of_admit.strftime('%B'), False)
                            department_dict[ipd.doctor_department_id.department][
                                ipd.date_of_admit.strftime('%B')] = old_value + 1
                        else:
                            department_dict[ipd.doctor_department_id.department][
                                ipd.date_of_admit.strftime('%B')] = 1
                    else:
                        department_dict[ipd.doctor_department_id.department] = {ipd.date_of_admit.strftime('%B'): 1}
                data = {
                    'select_years': self.select_years,
                    'start_date': self.start_date.strftime(user_date_format),
                    'end_date': self.end_date.strftime(user_date_format),
                    'record': department_dict,
                }
                return self.env.ref('IPD.action_ipd_month_reports').report_action(self, data=data)
            else:
                raise ValidationError("Record not found of this year")

        # --------------------------------ipd patient wise medicine report------------------------------------
        if self.start_date and self.end_date and self.select_report == 'group_by_medicine_patient':
            ipd_list = []
            for ipd in ipd_id:
                medicine_list = []
                for med in ipd.ipd_summary_line_ids:
                    for res in med.medicine_detail:
                        medicine_list.append(
                            [res.name, med.morning_dose, med.noon_dose, med.evening_dose, med.night_dose,
                             med.medicine_days])
                age = ipd.patient_id.age
                vals = {

                    'name': ipd.name,
                    'patient_id': ipd.patient_id.name,
                    'age': age,
                    'sex': ipd.patient_id.sex,
                    'doctor_department_id': ipd.doctor_department_id.department,
                    'doctor_id': ipd.doctor_id.name,
                    'medicine': medicine_list,
                    # 'morning_dose': med.morning_dose,
                    # 'morning_dose':med.morning_dose,
                    # 'morning_dose':med.morning_dose,
                    'date_of_admit': ipd.date_of_admit,
                }
                ipd_list.append(vals)
            data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'search_record': ipd_list
            }
            return self.env.ref('IPD.action_ipd_medicine_patient_reports').report_action(self, data=data)

        # -------------------------------------ipd patient count report-------------------------.
        if self.select_report == 'patient_count' and self.start_date and self.end_date:
            dis_ipd_id = self.env['ipd.registration'].sudo().search([('state', '=', 'discharge')])
            admission_dict = {}
            for rec in ipd_id:
                if rec.doctor_department_id.department in admission_dict:
                    if rec.patient_id.sex == 'male':
                        admission_dict[rec.doctor_department_id.department].update(
                            {'male': int(admission_dict[rec.doctor_department_id.department].get('male')) + 1, })
                    if rec.patient_id.sex == 'female':
                        admission_dict[rec.doctor_department_id.department].update(
                            {'female': int(admission_dict[rec.doctor_department_id.department].get('female')) + 1})
                else:
                    if rec.patient_id.sex == 'male':
                        admission_dict[rec.doctor_department_id.department] = {'male': 1, 'female': 0, 'dis_male': 0,
                                                                               'dis_female': 0}
                    if rec.patient_id.sex == 'female':
                        admission_dict[rec.doctor_department_id.department] = {'male': 0, 'female': 1, 'dis_male': 0,
                                                                               'dis_female': 0}
            for rec in dis_ipd_id:
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
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'search_record': admission_dict,
            }
            return self.env.ref('IPD.action_patient_count_reports').report_action(self, data=data)

        # --------------------------------ipd report (start_date end_date range)----------------------------
        if self.start_date and self.end_date:
            user_date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
            ipd_list = []
            for ipd in ipd_id:
                vals = {
                    'name': ipd.name,
                    'patient_id': ipd.patient_id.name,
                    # 'age': ipd.patient_id.age.split(',')[0],
                    'age': ipd.patient_id.age.split(',')[
                        0] if ipd.patient_id.age and ',' in ipd.patient_id.age else ipd.patient_id.age,
                    'sex': ipd.patient_id.sex,
                    'doctor_department_id': ipd.doctor_department_id.department,
                    'doctor_id': ipd.doctor_id.name,
                    'date_of_admit': ipd.date_of_admit,
                    'room_no': ipd.select_room_number.room_no,
                    'bed': ipd.bed_id.name,
                    'mobile': ipd.patient_id.mobile,
                }
                ipd_list.append(vals)
            data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'search_record': ipd_list
            }
            return self.env.ref('IPD.action_ipd_reports').report_action(self, data=data)
