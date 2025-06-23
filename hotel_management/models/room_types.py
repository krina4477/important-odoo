from odoo import models, fields, api


class RoomTypes(models.Model):
    _name = "room.types"

    name = fields.Char("Room Types")
    room_facility = fields.Text("Room Facility")
    room_ids = fields.Many2many("room.number", string="Room Number")
