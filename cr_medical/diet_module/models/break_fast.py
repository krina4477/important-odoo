from odoo import models, fields


class BreakFast(models.Model):
    _name = "break.fast"
    _rec_name = "name"
    _description = "Breakfast Information"

    name = fields.Char("Breakfast")
