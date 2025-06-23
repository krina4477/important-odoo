# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = "res.users"

    po_auto_complete = fields.Boolean('Purchase Order Auto Complete', default=False, copy=False)