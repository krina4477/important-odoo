from odoo import http, fields
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.portal.controllers import portal
import base64


class HotelManagement(http.Controller):

    @http.route('/hotel', type='http', auth='public', website=True)
    def my_route(self):
        hotel_history = request.env['booking.form'].sudo().search([])  # Fetch all booking form records

        return request.render('hotel_management.booking_template', {
            'hotel_history': hotel_history,

        })

    @http.route('/booking/<model("booking.form"):booking>', type='http', auth='public', website=True)
    def open_booking_form(self, booking):
        # booking = request.env['booking.form'].sudo().browse(booking_id)
        # add customer image
        # customer = booking.customer_id
        print(1111111111111, booking)

        return request.render('hotel_management.booking_form_template', {
            'booking': booking,
            # 'customer': customer,
        })

    @http.route('/customer/form', type='http', auth='public', website=True)
    def partner_form(self, **post):
        # Fetch available room numbers from room.number model
        room_numbers = request.env['room.number'].sudo().search([])
        room_types = request.env['room.types'].sudo().search([])  # Fetch all room types

        return request.render("hotel_management.customer_form_template", {
            'room_numbers': room_numbers,  # Pass the available room numbers to the template context
            'room_types': room_types,
        })

    @http.route(['/customer/form/submit'], type='http', auth="public", website=True)
    # next controller with url for submitting data from the form#
    def customer_form_submit(self, **post):
        print(111111111111111111111, post)
        # Extract data from the form fields
        name = post.get('name')
        check_in_date = post.get('check_in_date')
        check_out_date = post.get('check_out_date')
        room_number_id = post.get('room_number_id')
        room_facility = post.get('room_facility')
        booking_reference = post.get('booking_reference')
        type_ids = [int(type_id) for type_id in post.get('type_ids')]
        email = post.get('email')
        phone = post.get('phone')
        city = post.get('city')
        print("+++++++++++++++++", post.get('room_number_id'))
        print("+++++++++++++++++", room_number_id)

        # Check if the date strings are not empty
        if not check_in_date or not check_out_date:
            error_message = "Please provide valid check-in and check-out dates."
            return "<div style='text-align: center;'><h2>Error</h2><p>{}</p></div>".format(error_message)

        # Convert date strings to valid date objects
        check_in_date = fields.Date.from_string(check_in_date)
        check_out_date = fields.Date.from_string(check_out_date)

        # Find the customer's res.partner record based on the provided name
        customer = request.env['res.partner'].sudo().search([('name', '=', name)], limit=1)
        if not customer:
            # If the customer doesn't exist, create a new res.partner record for the customer
            customer = request.env['res.partner'].sudo().create({
                'name': name,
                'email': email,
                'phone': phone,
            })

        # Create a new booking.form record and link it to the customer
        booking = ({
            'customer_id': customer.id,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'room_number_ids': [(6, 0, [room_number_id])],
            'room_facility': room_facility,
            'booking_reference': booking_reference,
            'type_ids': [(6, 0, type_ids)],
            'city': city,
            'email': email,
            'phone': phone,
        })
        print(booking, 222222222222222)
        val = request.env['booking.form'].sudo().create(booking)

        # Render the template with the customer data
        return request.render("hotel_management.customer_form_success_tmp", {'val': val})

    @http.route(['/customer/form/cancel'], type='http', auth="public", website=True)
    def customer_form_cancel(self, **post):
        # Redirect back to the customer/form page without doing anything
        return request.redirect('/customer/form')

    # confirm booking of booking form template
    @http.route('/confirm_booking/<model("booking.form"):booking>', type='http', auth='public', website=True)
    def confirm_booking(self, booking):
        booking.confirm()
        return request.redirect('/booking/{}'.format(slug(booking)))

    @http.route('/cancel_booking/<model("booking.form"):booking>', type='http', auth='public', website=True)
    def cancel_booking(self, booking):
        booking.cancel()
        return request.redirect('/booking/{}'.format(slug(booking)))

    # def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
    #     self.ensure_one()
    #     url = self.access_url + '%s?access_token=%s%s%s%s%s' % (
    #         suffix if suffix else '',
    #         self._portal_ensure_token(),
    #         '&report_type=%s' % report_type if report_type else '',
    #         '&download=true' if download else '',
    #         query_string if query_string else '',
    #         '#%s' % anchor if anchor else ''
    #     )
    #     return url

    @http.route('/customer/form/download/<model("booking.form"):booking>', type='http', auth="public", website=True)
    def customer_form_download(self, booking):
        # Generate the PDF report for the booking and send it as a download response
        report = request.env.ref('hotel_management.action_report_booking').sudo()
        pdf_content, _ = report._render_qweb_pdf([booking.id])
        pdf_base64 = base64.b64encode(pdf_content)
        pdf_base64_str = pdf_base64.decode('utf-8')  # Convert bytes to string
        response = request.make_response(pdf_base64_str)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=Booking_Form.pdf'
        return response

    @http.route('/print/hotel_booking/<int:booking_id>', type='http', auth="public")
    def print_hotel_booking(self, booking_id, **kw):
        booking = request.env['booking.form'].browse(booking_id)
        return request.render('hotel_management.report_booking_document', {'doc': booking})


class CustomerPortal(portal.CustomerPortal):

    @http.route('/hotel', type='http', auth='public', website=True)
    def hotel_management_home(self):
        return request.redirect('/hotel')
