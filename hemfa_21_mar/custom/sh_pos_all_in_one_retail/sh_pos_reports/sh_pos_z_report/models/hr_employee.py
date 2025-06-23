# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sh_is_allow_z_report = fields.Boolean(string="Allow to Generate Z-Report ?")
