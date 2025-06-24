# -*- encoding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pathologist_education_ids = fields.Many2many("pathologist.education", string="Education")
    city = fields.Char("City")
    sex = fields.Selection([('male', 'Male'), ('female', 'Female')])
    is_pathologist = fields.Boolean('Is Lab Technician')


class education(models.Model):
    _name = "pathologist.education"
    _description = "Information About lab Pathologist's Education"

    name = fields.Char(string="Education Degree", required=True)
