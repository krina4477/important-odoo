from odoo import models, fields


class ConfirmReport(models.TransientModel):
    _name = "confirm.report"

    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")

    def confirm_report(self):
        domain = [
            ('check_in_date', '>=', self.start_date),
            ('check_out_date', '<=', self.end_date),
        ]
        bookings = self.env['booking.form'].search(domain)
        print(bookings)
        # Additional processing or manipulation of data can be done here before generating the report
        return self.env.ref('hotel_management.action_report_booking').report_action(bookings)
