from odoo import models, fields


class DinnerInfo(models.Model):
    _name = "dinner.info"
    _rec_name = "name"
    _description = "Dinner Information"

    name = fields.Char("Dinner")
