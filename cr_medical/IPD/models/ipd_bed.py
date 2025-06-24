from odoo import fields, models, api, _


class Bed(models.Model):
    _name = "bed.bed"
    _description = "Bed"

    name = fields.Char('Name')
    occupied = fields.Boolean('Occupied')
    room_obj = fields.Many2one('room.type', string="Room Object")
    opd_id = fields.Many2one('opd.opd')
    admit_patient_id = fields.Many2one('ipd.registration')
    date = fields.Date()
    seq = fields.Char()
