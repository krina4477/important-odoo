# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import models,api,fields,_


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    auto_create_employee = fields.Boolean(string='Auto Create Employee on User creation',related='company_id.auto_create_employee', readonly=False)
