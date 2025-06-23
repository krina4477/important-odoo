from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
from odoo.addons.http_routing.models.ir_http import slug


class BookingForm(models.Model):
    _name = "booking.form"
    _rec_name = "customer_id"
    _description = "Hotel Booking Form"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def set_default_number(self):
        return "New"

    number = fields.Char(default=set_default_number)
    booking_reference = fields.Char("Booking Reference")
    check_in_date = fields.Date("Check In Date")
    check_out_date = fields.Date("Check Out Date")
    customer_id = fields.Many2one("res.partner", string="Customer")
    room_number_ids = fields.Many2many("room.number", string="Room Number",
                                       domain="[('room_type_ids', 'in', type_ids)]", store=True)
    type_ids = fields.Many2many("room.types", string="Room Types")
    room_facility = fields.Text("Room Facility", compute="_compute_room_facility")
    phone = fields.Char(string="Phone", related="customer_id.phone")
    email = fields.Char(string="email", related="customer_id.email")
    city = fields.Selection(
        [('ahmedabad', 'Ahmedabad'), ('baroda', 'Baroda'), ('surat', 'Surat'), ('junagadh', 'Junagadh')])
    user_id = fields.Many2one('res.users')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('cancel', 'Cancelled')], string='Status',
                             readonly=True)

    @api.depends('type_ids')
    def _compute_room_facility(self):
        for booking in self:
            room_facilities = booking.type_ids.mapped('room_facility')
            booking.room_facility = '\n'.join(room_facilities)

    @api.constrains('check_in_date', 'check_out_date')
    def _check_date_validity(self):
        for booking in self:
            if booking.check_in_date < date.today():
                raise ValidationError("Check In Date cannot be in the past.")
            if booking.check_out_date < booking.check_in_date:
                raise ValidationError("Check Out Date must be after Check In Date.")
            if booking.check_in_date == booking.check_out_date:
                pass
                # Handling same day check-in and check-out
                # if not booking.room_number_ids:
                #     raise ValidationError("Please select at least one room number for the booking.")

    @api.constrains('room_number_ids')
    def _check_room_availability(self):
        for booking in self:
            booked_rooms = self.search([('room_number_ids', 'in', booking.room_number_ids.ids),
                                        ('check_out_date', '>=', booking.check_in_date),
                                        ('check_in_date', '<=', booking.check_out_date),
                                        ('id', '!=', booking.id),
                                        ('state', '!=', 'cancel')])
            if booked_rooms:
                raise ValidationError("Some of the selected rooms are already booked for the given dates.")

    @api.model
    def create(self, vals):
        vals['state'] = 'draft'
        vals['number'] = self.env['ir.sequence'].next_by_code('booking.number')
        booking = super(BookingForm, self).create(vals)
        booking_history_vals = {
            'booking_form': booking.id,
            'booking_reference': booking.booking_reference,
            'room_number_ids': [(6, 0, booking.room_number_ids.ids)],
            'customer_id': booking.customer_id.id,
            'check_in_date': booking.check_in_date,
            'check_out_date': booking.check_out_date,
        }
        self.env['booking.history'].sudo().create(booking_history_vals)
        return booking

    def draft(self):
        self.state = 'draft'

    def confirm(self):
        self.state = 'confirm'

    def cancel(self):
        self.state = 'cancel'
        print(2222)

    # generates a URL for the specific booking form record
    def action_preview_hotel(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        booking_url = '/booking/{}'.format(slug(self))

        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': base_url + booking_url,
        }
