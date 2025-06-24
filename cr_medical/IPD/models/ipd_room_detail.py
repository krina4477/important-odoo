# -*- coding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class room(models.Model):
    _inherit = "room"
    _description = "room"
    _rec_name = 'room_no'

    room_no = fields.Integer("Room Number", required=True)
    # floor_id = fields.Many2one("floor", string="Hotel Floor")
    room_type_id = fields.Many2one("room.type", string="Room Type")
    # booking_ids = fields.One2many("booking", "room_id")
    room_details = fields.Char('Room Description', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('selected', 'Selected'), ("not selected", "Not Selected")],
        string="Room Number", default='not selected')

    def disconfirm_state(self):
        self.state = 'selected'


class room_type(models.Model):
    _inherit = "room.type"
    _description = "room type"

    name = fields.Char(string='Room Type', required=True)
    facility_ids = fields.Many2many('room.facilities', required=True)
    price = fields.Integer(string="Price (In Rs.)", required=True)
    # room_id = fields.Many2one("room", string="Rooms", required=True)
    room_id = fields.One2many("room", "room_type_id", string="Rooms", required=True)
    no_of_bed = fields.Integer("No. of Bed")
    bed_ids = fields.One2many('bed.bed', 'room_obj', string="Beds")

    def generate_bed(self):
        for number in range(1, self.no_of_bed + 1):
            self.write({
                'bed_ids': [(0, None, {'name': 'Bed' + '-' + str(number)})]
            })


class room_facilities(models.Model):
    _name = "room.facilities"
    _description = "facilities"

    name = fields.Char(string="Facilities", required=True)
