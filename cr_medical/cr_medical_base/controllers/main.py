# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import Controller, request, route
import base64
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
import random


def random_token():
    chars = '0123456789'
    return ''.join(random.SystemRandom().choice(chars) for _ in range(8))


class Website(Controller):

    # ====================================== New Registration Patient Form =========================================================================
    @http.route(['/patient-from-test'], type='http', auth='public', website=True, csrf=False)
    def website_patient_save(self, **post):
        partner_rec = request.env['res.partner'].sudo().search([('email', '=', post.get('email'))])
        if partner_rec:
            return request.redirect('/registration-from-info')
        else:
            patient_info = request.env['res.partner'].sudo().create({
                'name': post.get('patient name'),
                'date_of_birth': post.get('Patient BirthDate'),
                'age': post.get('patient age'),
                'sex': post.get('sex'),
                'blood_group': post.get('blood_group'),
                'marital_status': post.get('marital_status'),
                'mobile': post.get('mobile number'),
                'email': post.get('email'),
                'street': post.get('street_name'),
                'street2': post.get('street2_name'),
                'city': post.get('city_name'),
                'state_id': int(post.get('state_id')),
                'zip': post.get('zip_name'),
                'country_id': int(post.get('country_id')),
                'is_patient': True,
                'state': 'pending',
                # 'valid' : 'valid'
            })
            tokan = random_token()
            confirmation_ref = tokan + str(patient_info.id)
            patient_info.write({'confirmation_ref': confirmation_ref})
            template = request.env.ref('cr_medical_base.registration_patient')
            template.sudo().update({
                'email_from': request.env.user.company_id.email,
                'email_to': post.get('email')
            })
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            template.with_context(user_name=post.get('patient name'),
                                  confirmation_ref=confirmation_ref).sudo().send_mail(patient_info.id, force_send=True)
            return request.render("cr_medical_base.thankyou_page_patient",
                                  {'confirmation_ref': confirmation_ref, 'base_url': base_url})

    # ====================================== New Registration Doctor Form =========================================================================
    @http.route(['/doctor-form-test'], type='http', auth='public', website=True, csrf=False)
    def doctor_demo_save(self, **post):

        temp = request.httprequest.form.getlist('speciality_name')
        temp2 = request.httprequest.form.getlist('degree_name')
        temp3 = request.httprequest.form.getlist('available_weekdays_name')

        files = request.httprequest.files.getlist('image')

        week_ids = request.env['weekday.name'].sudo().search([('name', 'in', temp3)])
        from_time_id = request.env['time.hours'].sudo().search([('name', '=', post.get('from_time_name'))])
        if not from_time_id:
            from_time_id = request.env['time.hours'].sudo().create({
                'name': post.get('from_time_name'),
                'time': float(post.get('from_time_name').replace(':', '.'))
            })

        to_time_id = request.env['time.hours'].sudo().search([('name', '=', post.get('to_time_name'))])
        if not to_time_id:
            to_time_id = request.env['time.hours'].sudo().create({
                'name': post.get('to_time_name'),
                'time': float(post.get('to_time_name').replace(':', '.'))
            })

        doctor_weekavailiblity = request.env["doctor.weeklyavalibility"].sudo().create({
            'available_weekdays': [(6, 0, week_ids.ids)],
            'from_time': from_time_id.id,
            'to_time': to_time_id.id,
            'totel_appointment': post.get('totel_appointment_name'),
            'name': post.get('total_time_name'),
        })
        user_rec_1 = request.env['res.users'].sudo().search(
            [('login', '=', post.get('email_name'))])

        if user_rec_1:
            return request.redirect('/registration-from-info')

        else:
            doctor_info = request.env['res.partner'].sudo().create({
                'name': post.get('doctor_name'),
                'image_1920': base64.encodestring(files[0].read()),
                # 'speciality_ids': post.get('speciality_name'),
                'joining_date': post.get('Doctor_Joining_Date'),
                'sex': post.get('sex'),
                'doctor_fees': post.get('doctor_fees'),
                'licence': post.get('licence_id'),
                # 'degree_ids': post.get('degree_name'),
                'working_institute': post.get('working_institute'),
                'mobile': post.get('mobile'),
                'email': post.get('email_name'),
                'work_location': post.get('working_location'),
                'is_doctor': True,
                'state': 'pending',
                'weekly_avalibility_line': [(6, 0, [doctor_weekavailiblity.id])],  # for One2Many Relation
                'speciality_ids': [(6, 0, [speciality1 for speciality1 in temp])],
                'degree_ids': [(6, 0, [degree1 for degree1 in temp2])],

            })
            return request.redirect('/thank-you')

    # ====================================== Make Appointment Form Data =========================================================================
    @http.route(['/opd-form-info'], type='http', auth='public', website=True)
    def website_opd(self, **post):
        patient_data = request.env['res.partner'].sudo().search([('is_patient', '=', True), ("state", "=", "approve")])
        doctor_data = request.env['res.partner'].sudo().search([('is_doctor', '=', True), ("state", "=", "approve")])
        state_name = request.env['res.country.state'].sudo().search([])
        country_name = request.env['res.country'].sudo().search([])
        time_data = request.env['doctor.weeklyavalibility'].sudo().search([])
        return request.render("cr_medical_base.website_opd_form",
                              {'patient_data': patient_data, 'doctor_data': doctor_data, 'time_data': time_data,
                               'res_data_state': state_name,
                               'res_data_country': country_name, })

    # ====================================== Email Check =========================================================================
    @route('/test/email', type='json', auth='public', csrf=False)
    def email(self, email, **kwargs):
        partner_id = request.env['res.partner'].sudo().search([('email', '=', email)])
        if partner_id:
            return True
        else:
            return False

    # ====================================== Email Check =========================================================================
    @route('/test/licence_id', type='json', auth='public', csrf=False)
    def Licence_Id_Check(self, licence_id, **kwargs):
        partner_id = request.env['res.partner'].sudo().search([('licence', '=', licence_id)])
        if partner_id:
            return True
        else:
            return False

    # ====================================== Make Appointment in Patient List =========================================================================
    @route('/test/patient_id', type='json', auth='public', csrf=False)
    def patient_info(self, confirmation_ref, **kwargs):
        partner_id = request.env['res.partner'].sudo().search(
            ['|', ('confirmation_ref', 'ilike', confirmation_ref), ('name', 'ilike', confirmation_ref),
             ('state', '=', 'approve'), ('is_patient', '=', True)])
        return dict(states=[(partner.id, partner.name) for partner in partner_id])

    # ====================================== Make Appointment in Available Day =========================================================================
    @http.route(['/test/day_infos'], type='json', auth="public", methods=['POST'], website=True)
    def day_infos(self, doctor_data, **kw):
        day_ids = request.env['doctor.weeklyavalibility'].sudo().search([('doctor_id', '=', int(doctor_data))])
        list_val = []
        for a in day_ids:
            for b in a.available_weekdays:
                name = b.name
                time = b.name + ' , ' + str(a.from_time.name) + ' to ' + str(a.to_time.name)
                t = tuple()
                l = list(t)
                l.append(name)
                l.append(time)
                list_val.append(tuple(l))
        return dict(days=list_val)

    # ====================================== Make Appointment in Select Time =========================================================================
    @http.route(['/test/selecttime_infos'], type='json', auth="public", methods=['POST'], website=True)
    def selecttime_infos(self, availabel_days, doctor_data, **kw):
        week_ids = request.env['weekday.name'].sudo().search([('name', '=', availabel_days)])
        selecttime_ids = request.env['doctor.weeklyavalibility'].sudo().search(
            [('doctor_id', '=', int(doctor_data)), ('available_weekdays', 'in', week_ids.ids)])
        selecttime = []
        for week in selecttime_ids:
            total_time = week.from_time.time
            while total_time:
                if total_time >= week.to_time.time:
                    break
                name = str(total_time).replace('.', ':') + ' To ' + str(total_time + 1).replace('.', ':')
                total_time += 1
                selecttime.append((week.id, name))
        return dict(
            selecttime=selecttime  # [(st.id, st.name) for st in selecttime_ids],
        )

    # ====================================== Make Appointment Existing Patient =========================================================================
    @http.route(['/website-opd-test'], type='http', auth='public', website=True, csrf=False)
    def website_opd_save_existing(self, **post):
        if not post.get('doctor_id'):
            return request.redirect('/opd-form-info')

        week_id = request.env['weekday.name'].sudo().search([('name', '=', post.get('weekdays_name'))])
        doctor_data1 = request.env["doctor.weeklyavalibility"].sudo().search(
            [('doctor_id', '=', int(post.get('doctor_id'))), ('available_weekdays', 'in', week_id.ids),
             ('id', '=', post.get('select_time_id'))])
        data = request.env['res.partner'].sudo().search(
            [('is_doctor', '=', True), ('id', '=', int(post.get('doctor_id')))])

        for j in data.weekly_avalibility_line:
            opd_record = request.env['opd.opd'].search_count(
                [('weekdays', '=', post.get('weekdays_name')), ('doctor_id', '=', data.id),
                 ('select_time_id', '=', doctor_data1.name),
                 ('appointment_date', '=', post.get('appointment_date_name'))
                    , ('state', 'in', ['pending', 'confirm'])])

            if (doctor_data1.totel_appointment > opd_record):
                opd_data = request.env['opd.opd'].sudo().create({
                    'patient_id': int(post.get('patient_name')),
                    'doctor_id': data.id,
                    'doctor_department_id': data.doctor_department_id.id,
                    'appointment_date': post.get('appointment_date_name'),
                    'available_day': post.get('availabel_days'),
                    'weekdays': post.get('weekdays_name'),
                    'select_time_id': int(post.get('select_time_id')),
                    'existing_patient_name': True,
                    'state': 'pending',
                    'is_normal_opd': True,
                })
                return request.redirect('/thank-you')

    # ====================================== Make Appointment New Patient =========================================================================
    @http.route(['/website-opd-new-test'], type='http', auth='public', website=True, csrf=False)
    def website_opd_save_new(self, **post):
        partner_rec = request.env['res.partner'].sudo().search([('email', '=', post.get('email'))])
        if not post.get('doctor_id_new'):
            return request.redirect('/opd-form-info')
        data = request.env['res.partner'].sudo().search(
            [('is_doctor', '=', True), ('id', '=', int(post.get('doctor_id_new')))])
        select_time_id_new = request.env['doctor.weeklyavalibility'].sudo().search(
            [('id', '=', int(post.get('select_time_id_new')))])

        if partner_rec:
            return request.redirect('/opd-form-info')
        else:
            opd_data = request.env['opd.opd'].sudo().create({
                'new_patient_name': post.get('patient_name_name'),
                'street': post.get('street_name'),
                'street2': post.get('street2_name'),
                'country_id': int(post.get('country_id')),
                'state_id': int(post.get('state_id')),
                'city': post.get('city_name'),
                'zip': post.get('zip_name'),
                'date_of_birth': post.get('date_of_birth_name'),
                'age': post.get('age_name'),
                'sex': post.get('sex'),
                'blood_group': post.get('blood_group'),
                'mobile': post.get('mobile_number'),
                'email': post.get('email'),
                'doctor_id': data.id,
                'available_day': post.get('available_day_new'),
                'appointment_date': post.get('appointment_date_name1'),
                'doctor_department_id': post.get('appointment_date_name1'),
                'select_time_id': select_time_id_new.id,
                'weekdays': post.get('weekdays_name'),
                'patient_id': post.get('patient_id'),
                'create_new_patient_button': True,
            })
            patient_info = opd_data.sudo().create_new_patient()
            opd_data.sudo().write({"patient_id": patient_info.id})
            tokan = random_token()
            confirmation_ref = tokan + str(patient_info.id)
            patient_info.write({'confirmation_ref': confirmation_ref, 'marital_status': post.get('marital_status')})
            template = request.env.ref('cr_medical_base.registration_patient_and_appointment')
            template.sudo().update({
                'email_from': request.env.user.company_id.email,
                'email_to': post.get('email')
            })
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            template.with_context(user_name=post.get('patient name'), confirmation_ref=confirmation_ref,
                                  appointment_date=post.get('appointment_date_name1')).sudo().send_mail(patient_info.id,
                                                                                                        force_send=True)
            return request.render("cr_medical_base.thankyou_page_patient",
                                  {'confirmation_ref': confirmation_ref, 'base_url': base_url})

    # ====================================== Registration Form Data =========================================================================
    @http.route(['/registration-from-info'], type='http', auth='public', website=True)
    def website_registration_form1(self, **post):
        res_data = request.env['res.partner'].sudo().search([('is_patient', '=', True)])
        country = request.env['res.country'].sudo().search([])
        res_data1 = request.env['res.partner'].sudo().search([('is_doctor', '=', True)])
        speciality_data = request.env["doctor.speciality"].sudo().search([])
        degree_data = request.env["doctor.degree"].sudo().search([])
        user_rec = request.env['res.users'].sudo().search([('login', '=', post.get('email'))])
        valid = False

        return request.render("cr_medical_base.website_registration_form",
                              {'res_data': res_data,
                               'countries': country,  # doc
                               'res_data1': res_data1,
                               'degree_data': degree_data,
                               'speciality_data': speciality_data,
                               'valid': valid,
                               })

    # ====================================== State Data =========================================================================
    @http.route(['/country_infos/<model("res.country"):country>'], type='json', auth="public", methods=['POST'],
                website=True)
    def country_infos(self, country, **kw):
        states_ids = request.env['res.country.state'].sudo().search([('country_id', '=', country.id)])
        states = [(st.id, st.name, st.code) for st in states_ids]

        return dict(
            states=[(st.id, st.name, st.code) for st in states_ids],
        )

    # ====================================== Doctor Informations =========================================================================
    @http.route(['/doctor-info'], type='http', auth='public', website=True)
    def doctor_view(self):
        record_boolean = False
        doctor_data = request.env['res.partner'].sudo().search([('is_doctor', '=', True), ('state', '=', 'approve')])
        if doctor_data:
            record_boolean = True
        speciality_data = request.env["doctor.speciality"].sudo().search([])
        return request.render("cr_medical_base.website_doctor_template",
                              {'doctor_data': doctor_data, 'record_boolean': record_boolean,
                               'speciality_data': speciality_data})

    # ====================================== Meet the Doctor And Book Appointment =========================================================================
    @http.route(['/candidroot_medical/doctor-details-info/<int:doctor>'], type='http', auth="public", website=True)
    def docturinfo(self, doctor, **kw):
        doctor_id = request.env['res.partner'].sudo().browse(doctor)
        return request.render("cr_medical_base.website_doctor_details_template", {'data': doctor_id})


class WebsiteDemo(Controller):
    @route(['/website-demo'], type='http', auth='user', website=True)
    def website_demo_view(self, **post):
        res_data = request.env['res.partner'].sudo().search([('is_patient', '=', True)])
        state_name = request.env['res.country.state'].sudo().search([])
        country_name = request.env['res.country'].sudo().search([])
        return request.render("cr_medical_base.website_demo",
                              {'res_data': res_data, 'res_data_state': state_name, 'res_data_country': country_name})


class Dashboard(Controller):
    @http.route('/web/view/edit_custom', type='json', auth="user")
    def edit_custom(self, arch):
        return {'result': True}
