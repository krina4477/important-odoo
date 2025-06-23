from odoo import http, fields
from odoo.http import request
from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):

    @http.route('/course', type='http', auth='public', website=True)
    def my_route(self):
        hotel_history = request.env['course.info'].sudo().search([])  # Fetch

        return request.render('school_management.order_template', {
            'hotel_history': hotel_history,

        })

    # @http.route('/course/<int:course_id>', type='http', auth='public', website=True)
    # def open_course_details(self, course_id):
    #     course = request.env['course.info'].sudo().browse(course_id)
    #     # You can add more data if needed, like fetching customer info related to this course
    #
    #     return request.render('school_management.course_template', {
    #         'course': course,
    #     })

    @http.route(['/course_shop'], type='http', auth="public", website=True)
    def course(self):
        course = request.env['course.info'].sudo()
        obj = course.search([])
        values = {
            'course': obj

        }
        return request.render('school_management.shop_template', values)
