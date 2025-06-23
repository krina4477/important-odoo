# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import fields, models

class IrModelFieldsCr(models.Model):
    _inherit = 'ir.model.fields'

    is_custom_field = fields.Boolean('Is Custom Field')
