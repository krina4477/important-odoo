from odoo import http, _
from odoo.http import Controller, request, route
import base64
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
import random


class PortalAccount(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'opd_count' in counters:
            if request.env.user.partner_id.is_doctor:
                doctor_opd_count = request.env['opd.opd'].search_count(
                    [('doctor_id.user_id', '=', request.uid), ('is_normal_opd', '=', True)])
                values['opd_count'] = doctor_opd_count
            else:
                patient_opd_count = request.env['opd.opd'].search_count(
                    [('patient_id.user_id', '=', request.uid), ('is_normal_opd', '=', True)])
                values['opd_count'] = patient_opd_count

        if 'pharmacy_count' in counters:
            if request.env.user.partner_id.is_doctor:
                doctor_pharmacy_count = request.env['pharmacy.prescription'].sudo().search_count(
                    [('doctor_id.user_id', '=', request.uid)])
                values['pharmacy_count'] = doctor_pharmacy_count
            else:
                patient_pharmacy_count = request.env['pharmacy.prescription'].sudo().search_count(
                    [('patient_id.user_id', '=', request.uid)])
                values['pharmacy_count'] = patient_pharmacy_count

        if 'radiology_count' in counters:
            if request.env.user.partner_id.is_doctor:
                doctor_radiology_count = request.env['radiology.prescription'].sudo().search_count(
                    [('doctor_id.user_id', '=', request.uid)])
                values['radiology_count'] = doctor_radiology_count
            else:
                patient_radiology_count = request.env['radiology.prescription'].sudo().search_count(
                    [('patient_id.user_id', '=', request.uid)])
                values['radiology_count'] = patient_radiology_count

        if 'laboratory_count' in counters:
            if request.env.user.partner_id.is_doctor:
                doctor_laboratory_count = request.env['laboratory.prescription'].sudo().search_count(
                    [('doctor_id.user_id', '=', request.uid)])
                values['laboratory_count'] = doctor_laboratory_count
            else:
                patient_laboratory_count = request.env['laboratory.prescription'].sudo().search_count(
                    [('patient_id.user_id', '=', request.uid)])
                values['laboratory_count'] = patient_laboratory_count

        if 'ipd_count' in counters:
            if request.env.user.partner_id.is_doctor:
                doctor_ipd_count = request.env['ipd.registration'].sudo().search_count(
                    [('doctor_id.user_id', '=', request.uid)])
                values['ipd_count'] = doctor_ipd_count
            else:
                patient_ipd_count = request.env['ipd.registration'].sudo().search_count(
                    [('patient_id.user_id', '=', request.uid)])
                values['ipd_count'] = patient_ipd_count

        return values

    def _opd_get_page_view_values(self, opd, access_token, **kwargs):
        values = {
            'page_name': 'OPDs',
            'opd': opd,
        }
        return self._get_page_view_values(opd, access_token, values, 'my_opd_history', False, **kwargs)

    # ======================================Own OPD Tree view ==================================

    @http.route(['/my/all-opd'], type='http', auth="user", website=True)
    def user_own_all_opd(self, **kw):
        if request.env.user.partner_id.is_doctor:
            doctor_opd_ids = request.env['opd.opd'].sudo().search(
                [('doctor_id.user_id', '=', request.uid), ('is_normal_opd', '=', True)])
            value = {
                'opd_ids': doctor_opd_ids,
                'page_name': "OPDs",
            }
            return request.render("cr_medical_base.cr_medical_opd_tree_view_portal_user", value)

        if request.env.user.partner_id.is_patient:
            patient_opd_ids = request.env['opd.opd'].sudo().search(
                [('patient_id.user_id', '=', request.uid), ('is_normal_opd', '=', True)])
            value = {
                'opd_ids': patient_opd_ids,
                'page_name': "OPDs",
            }
            return request.render("cr_medical_base.cr_medical_opd_tree_view_portal_user", value)

    # =============================Own Pharmacy Tree view=================================================

    @http.route(['/my/all-pharmacy'], type='http', auth="user", website=True)
    def user_own_all_pharmacy(self, **kw):
        if request.env.user.partner_id.is_doctor:
            doctor_pharmacy_ids = request.env['pharmacy.prescription'].sudo().search(
                [('doctor_id.user_id', '=', request.uid)])
            value = {
                'pharmacy_ids': doctor_pharmacy_ids,
                'page_name': "Pharmacy",
            }
            return request.render("cr_medical_base.cr_medical_pharmacy_portal_user", value)

        if request.env.user.partner_id.is_patient:
            patient_pharmacy_ids = request.env['pharmacy.prescription'].sudo().search(
                [('patient_id.user_id', '=', request.uid)])
            value = {
                'pharmacy_ids': patient_pharmacy_ids,
                'page_name': "Pharmacy",
            }
            return request.render("cr_medical_base.cr_medical_pharmacy_portal_user", value)

    # =============================Own Radiology Tree view=================================================
    @http.route(['/my/all-radiology'], type='http', auth="user", website=True)
    def user_own_all_radiology(self, **kw):
        if request.env.user.partner_id.is_doctor:
            doctor_radiology_ids = request.env['radiology.prescription'].sudo().search(
                [('doctor_id.user_id', '=', request.uid)])
            value = {
                'radiology_ids': doctor_radiology_ids,
                'page_name': "Radiology",

            }
            return request.render("cr_medical_base.cr_medical_radiology_portal_user", value)

        if request.env.user.partner_id.is_patient:
            patient_radiology_ids = request.env['radiology.prescription'].sudo().search(
                [('patient_id.user_id', '=', request.uid)])
            value = {
                'radiology_ids': patient_radiology_ids,
                'page_name': "Radiology",

            }
            return request.render("cr_medical_base.cr_medical_radiology_portal_user", value)

    # =============================Own Laboratory Tree view=================================================
    @http.route(['/my/all-laboratory'], type='http', auth="user", website=True)
    def user_own_all_laboratory(self, **kw):
        if request.env.user.partner_id.is_doctor:
            doctor_laboratory_ids = request.env['laboratory.prescription'].sudo().search(
                [('doctor_id.user_id', '=', request.uid)])
            value = {
                'laboratory_ids': doctor_laboratory_ids,
                'page_name': "Laboratory",

            }
            return request.render("cr_medical_base.cr_medical_laboratory_portal_user", value)

        if request.env.user.partner_id.is_patient:
            patient_laboratory_ids = request.env['laboratory.prescription'].sudo().search(
                [('patient_id.user_id', '=', request.uid)])
            value = {
                'laboratory_ids': patient_laboratory_ids,
                'page_name': "Laboratory",

            }
            return request.render("cr_medical_base.cr_medical_laboratory_portal_user", value)

    # =============================Own IPDs Tree view=================================================
    @http.route(['/my/all-ipd'], type='http', auth="user", website=True)
    def user_own_all_ipd(self, **kw):
        if request.env.user.partner_id.is_doctor:
            doctor_ipd_ids = request.env['ipd.registration'].sudo().search(
                [('doctor_id.user_id', '=', request.uid)])
            value = {
                'ipd_ids': doctor_ipd_ids,
                'page_name': "IPDs",

            }
            return request.render("cr_medical_base.cr_medical_ipd_portal_user", value)

        if request.env.user.partner_id.is_patient:
            patient_ipd_ids = request.env['ipd.registration'].sudo().search(
                [('patient_id.user_id', '=', request.uid)])
            value = {
                'ipd_ids': patient_ipd_ids,
                'page_name': "IPDs",

            }
            return request.render("cr_medical_base.cr_medical_ipd_portal_user", value)

    # =============================Own OPD Form view=================================================

    @http.route(['/my/opd/<int:opd_id>'], type='http', auth="user", website=True)
    def portal_my_opd_detail(self, opd_id, access_token=None, report_type=None, download=False, **kw):
        try:
            opd_sudo = self._document_check_access('opd.opd', opd_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._opd_get_page_view_values(opd_sudo, access_token, **kw)

        return request.render("cr_medical_base.cr_medical_opd_form_view_portal_user", values)

    # =============================Own Follow Up OPD Tree view=================================================

    @http.route(['/my/followup-opds/<int:follow_opds>'], type='http', auth="user", website=True)
    def user_follow_up_opd(self, follow_opds, **kw):
        follow_opd_id = request.env['opd.opd'].sudo().browse(int(follow_opds))
        if request.env.user.partner_id.is_patient:
            patient_follow_opds = request.env['opd.opd'].sudo().search(
                [('opd_id', '=', follow_opds), ('is_follow_up_opd', '=', True)])
            value = {
                'opd_ids': patient_follow_opds,
                'page_name': 'follow_opd',
                'follow_opd': follow_opds,
                'follow_opd_id': follow_opd_id,
            }
            return request.render("cr_medical_base.cr_medical_follow_up_opd_tree_view_portal_user", value)

        if request.env.user.partner_id.is_doctor:
            doctor_follow_opds = request.env['opd.opd'].sudo().search(
                [('patient_id', '=', follow_opd_id.patient_id.id), ('opd_id', '=', follow_opds),
                 ('is_follow_up_opd', '=', True)])
            value = {
                'opd_ids': doctor_follow_opds,
                'page_name': 'follow_opd',
                'follow_opd': follow_opds,
                'follow_opd_id': follow_opd_id,
            }
            return request.render("cr_medical_base.cr_medical_follow_up_opd_tree_view_portal_user", value)

    # =============================Own Follow Up OPD Form view=================================================

    @http.route(['/my/followup/<int:follow_opd_id>/<int:opd_id>'], type='http', auth="user", website=True)
    def portal_my_follow_opd_detail(self, follow_opd_id, opd_id, access_token=None, report_type=None, download=False,
                                    **kw):
        try:
            opd_sudo = self._document_check_access('opd.opd', opd_id, access_token)
            follow_opd_id = self._document_check_access('opd.opd', follow_opd_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        value = {
            'page_name': 'follow_opd',
            'follow_opd_id': follow_opd_id,
            'follow_opd_id_form': opd_sudo,
        }
        return request.render("cr_medical_base.cr_medical_followup_opd_form_view_portal_user", value)

    # =============================Own Pharmacy Form view=================================================

    @http.route(['/my/pharmacy/<int:pharmacy>'], type='http', auth="user", website=True)
    def user_pharmacy_details(self, pharmacy, **kw):
        pharmacy_id = request.env['pharmacy.prescription'].sudo().browse(pharmacy)
        value = {
            'pharmacy_id': pharmacy_id,
            'page_name': 'Pharmacy'
        }
        return request.render("cr_medical_base.cr_medical_pharmacy_form_view_portal_user", value)

    # =============================Own Radiology Form view=================================================

    @http.route(['/my/radiology/<int:radiology>'], type='http', auth="user", website=True)
    def user_radiology_details(self, radiology, **kw):
        radiology_id = request.env['radiology.prescription'].sudo().browse(radiology)
        value = {
            'radiology_id': radiology_id,
            'page_name': 'Radiology'

        }
        return request.render("cr_medical_base.cr_medical_radiology_form_view_portal_user", value)

    # =============================Own Laboratory Form view=================================================

    @http.route(['/my/laboratory/<int:laboratory>'], type='http', auth="user", website=True)
    def user_laboratory_details(self, laboratory, **kw):
        laboratory_id = request.env['laboratory.prescription'].sudo().browse(laboratory)
        value = {
            'laboratory_id': laboratory_id,
            'page_name': 'Laboratory'

        }
        return request.render("cr_medical_base.cr_medical_laboratory_form_view_portal_user", value)

    # =============================Own IPD Form view=================================================

    @http.route(['/my/ipd/<int:ipd>'], type='http', auth="user", website=True)
    def user_ipd_details(self, ipd, **kw):
        ipd_id = request.env['ipd.registration'].sudo().browse(ipd)
        value = {
            'ipd_id': ipd_id,
            'page_name': 'IPDs'

        }
        return request.render("cr_medical_base.cr_medical_ipd_form_view_portal_user", value)

    @http.route(['/my/review/<int:opd_id>'], type='http', auth="user", website=True)
    def user_ipd_details(self, opd_id, **kw):
        opd = request.env['opd.opd'].sudo().search([('id', '=', opd_id)])
        value = {
            'page_name': 'Preview',
            'opd_id': opd.id,
            'opd_name': opd.name,
            'patient_name': opd.patient_id.name,
            'doctor_name': opd.doctor_id.name,
            'Appointment_date': opd.appointment_date,
            'weekdays_name': opd.weekdays
        }
        return request.render("cr_medical_base.website_review_form", value)

    @http.route(['/website-review-patient'], type='http', auth="user", website=True, csrf=False)
    def get_rating_details(self, **post):
        rating_data = {
            'rating': post.get('rating'),
            'feedback': post.get('message'),
            'opd_id': post.get('opd_id')
        }

        if rating_data.get('opd_id', False):
            opd_id = int(rating_data.get('opd_id'))
            opd_object = request.env['opd.opd'].sudo().search([('id', '=', opd_id)])
            opd_object.write({
                'ratings': rating_data.get('rating', False),
                'feedback': rating_data.get('feedback', False),
            })
            return request.redirect("my/home")
