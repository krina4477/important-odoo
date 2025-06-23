# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.http import request

class IrHttpCr(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        info = super().session_info()
        info["group_global_custom_field"] = request.env.user.has_group('all_model_custom_fields_cr.group_global_custom_field')
        return info