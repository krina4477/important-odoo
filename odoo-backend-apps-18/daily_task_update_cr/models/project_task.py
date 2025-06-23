# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import fields, models

class ProjectTask(models.Model):

    _inherit = "project.task"

    manager_id = fields.Many2one("res.users", related="project_id.user_id")