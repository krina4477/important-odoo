# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from datetime import date, timedelta
import base64


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def send_employee_payslip_cron(self):
        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

        payslip_ids = self.env['hr.payslip'].sudo().search([('date_from', '>=', start_day_of_prev_month),
                                                            ('date_to', '<=', last_day_of_prev_month),
                                                            ('state', 'in', ['done', 'paid']), ])

        employee_dict_list = {}
        for payslip in payslip_ids:
            if payslip.employee_id not in employee_dict_list:
                employee_dict_list[payslip.employee_id] = [payslip]
            else:
                employee_dict_list[payslip.employee_id].append(payslip)
        for rec in employee_dict_list:
            attachment = []
            for payslip_id in employee_dict_list.get(rec):
                pdf_file = \
                    self.env['ir.actions.report']._render_qweb_pdf("hr_payroll.action_report_payslip", payslip_id.id)[0]
                pdf_file = base64.b64encode(pdf_file)
                filename = rec.name + ' Payslip' + ' ' + str(payslip_id.id) + '.pdf'
                payslip_data = self.env['ir.attachment'].create({
                    'name': filename,
                    'datas': pdf_file,
                    'type': 'binary',
                    'res_model': 'hr.payslip',
                    'res_id': payslip_id.id,
                    'store_fname': filename,
                    'mimetype': 'application/pdf',
                })
                attachment.append(payslip_data.id)
            template_id = self.env.ref('cr_auto_send_salaryslip.email_template_emp_payslip').id
            template = self.env['mail.template'].browse(template_id)
            email_values = {'email_to': rec.work_email, 'email_from': self.env.user.email_formatted,
                            'attachment_ids': attachment}
            template.send_mail(rec.id, email_values=email_values, force_send=True)
