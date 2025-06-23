from odoo import models, fields, api


class BookingHistory(models.Model):
    _name = "booking.history"
    _rec_name = "customer_id"

    def set_default_number(self):
        return "New"

    number = fields.Char(default=set_default_number)
    booking_form = fields.Many2one('booking.form', string="Booking Form", readonly=True)
    booking_reference = fields.Char("Booking Reference")
    room_number_ids = fields.Many2many("room.number", string="Room Number", readonly=True)
    customer_id = fields.Many2one("res.partner", readonly=True)
    check_in_date = fields.Date("Check In Date", readonly=True)
    check_out_date = fields.Date("Check Out Date", readonly=True)
    phone = fields.Char(string="Phone", related="customer_id.phone")
    email = fields.Char(string="email", related="customer_id.email")
    facility = fields.Text("Room Facility", related="booking_form.room_facility", readonly=True)
    booked_with = fields.Char("Booked With", compute="_compute_booked_with", readonly=True)
    booking_date = fields.Datetime("Booking Date", compute="_compute_booking_date", readonly=True)

    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('history.number')
        vals = super(BookingHistory, self).create(vals)
        return vals

    @api.depends('booking_form')
    def _compute_booked_with(self):
        for history in self:
            history.booked_with = history.booking_form.number

    @api.depends('booking_form')
    def _compute_booking_date(self):
        for history in self:
            history.booking_date = history.booking_form.create_date
