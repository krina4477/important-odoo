from odoo import models, fields


class SurgeryType(models.Model):
    _name = 'surgery.type'
    _rec_name = "surgery_type"

    surgery_type = fields.Char(string="Surgery Type")
