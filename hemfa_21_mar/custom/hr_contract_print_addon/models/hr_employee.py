from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    name_ar = fields.Char(string='Arabic Name', tracking=True)
    job_grade = fields.Char(string='Grade')
    institution = fields.Char(string='Institution')
    graduation_date = fields.Date(string='Graduation Date')


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    name_ar = fields.Char(string='Arabic Name', tracking=True)
    job_grade = fields.Char(string='Grade')
    institution = fields.Char(string='Institution')
    graduation_date = fields.Date(string='Graduation Date')
