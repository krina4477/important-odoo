# -*- encoding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pharmacist_education_ids = fields.Many2many("pharmacist.education", string="Education")
    city = fields.Char("City")
    sex = fields.Selection([('male', 'Male'), ('female', 'Female')])
    is_pharmacist = fields.Boolean('Is Pharmacist')


class Education(models.Model):
    _name = "pharmacist.education"
    _description = "Information About pharmacist's Education"

    name = fields.Char(string="EducationDegree", required=True)
