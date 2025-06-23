# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields
from lxml import etree


class DynamicFilterModel(models.Model):
    _name = 'dynamic.filter.model'
    _description = 'Dynamic Filter Model'

    name = fields.Char('Filter Name')

