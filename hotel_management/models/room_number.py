from odoo import models, fields, api


class RoomNumber(models.Model):
    _name = "room.number"
    _rec_name = "room_number"

    room_number = fields.Integer("Room Number")
    room_type_ids = fields.Many2many("room.types", string="Room Types")
