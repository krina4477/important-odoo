from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    birthday = fields.Date(required=True)
