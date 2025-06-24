from odoo import models, fields


class LunchInfo(models.Model):
    _name = "lunch.info"
    _rec_name = "name"
    _description = "Lunch Information"

    name = fields.Char("Lunch")
