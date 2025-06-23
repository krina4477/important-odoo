# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class CompareRecord(models.TransientModel):

    _name = 'wiz.compare.record'
    _description = 'Wiz Compare Record'

    compare_record_ids = fields.One2many('wiz.compare.record.fields','compare_record_id', string="Compare Record")


class CompareRecord(models.TransientModel):

    _name = 'wiz.compare.record.fields'
    _description = 'Wiz Compare Record'

    compare_record_id = fields.Many2one('wiz.compare.record', string="Compare Record")
    check_field = fields.Char(string='Check Field')
    old_value = fields.Char(string="Record1 Value")
    new_value = fields.Char(string="Record2 Value")
