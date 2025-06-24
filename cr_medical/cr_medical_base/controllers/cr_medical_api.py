# -*- coding: utf-8 -*-

import random
from datetime import datetime

from odoo import http
from odoo.http import request
from odoo.tools.image import image_data_uri


def random_token():
    chars = '0123456789'
    return ''.join(random.SystemRandom().choice(chars) for _ in range(8))


class AndroidApi(http.Controller):

    @http.route(['/medical'], type='json', auth='public', website=True)
    def index(self):
        if 'params' in request.jsonrequest:
            return getattr(self, request.jsonrequest['method'])(
                request.jsonrequest['params'])
        else:
            return getattr(self, request.jsonrequest['method'])()

    def registration_patient(self, params):
        """
            method: registration_patient
            "params:{
                "image",
                "name",
                "date_of_birth",
                "marital_status",
                "sex",
                "blood_group",
                "doctor_department_id",
                "doctor_id",
                "street",
                "street2",
                "city",
                "state_id",
                "country_id",
                "email",
                "mobile",
            }
        """
        user_id = request.env['res.users'].sudo().search([('login', '=', params.get('email'))])

        vals = {
            "image_1920": params.get("image"),
            "name": params.get("name"),
            "date_of_birth": params.get("date_of_birth"),
            "sex": params.get("sex"),
            "marital_status": params.get("marital_status"),
            "blood_group": params.get("blood_group"),
            # "doctor_department_id": params.get("doctor_department_id"),
            # "doctor_id": params.get("doctor_id"),
            "street": params.get("street"),
            "street2": params.get("street2"),
            "city": params.get("city"),
            "state_id": params.get("state_id.name"),
            "country_id": params.get("country_id.name"),
            "email": params.get("email"),
            "mobile": params.get("mobile"),
            "is_patient": True,
            "state": "pending",
        }
        if not user_id:
            create_patient = request.env['res.partner'].sudo().create(vals)
            create_patient.create_user()
            return {'type': "success", "message": " Patient Created Successfully"}
        else:
            return {"type": "error", "message": "This patient is Already Register "}

    def registration_doctor(self, params):
        """
            "method": registration_doctor.
            "params":{
                "image_1920",
                "name",
                "speciality_ids",
                "joining_date",
                "sex",
                "degree_ids",
                "doctor_fees",
                "doctor_department_id",
                "registration_no",
                "total_experience",
                "working_institute",
                "doctor_description",
                "sign_by",
                "email",
                "mobile",
                "language"
            }
        """
        user_id = request.env['res.users'].sudo().search([('login', '=', params.get('email'))])
        vals = {
            "image_1920": params.get("image"),
            "name": params.get("name"),
            "speciality_ids": params.get("speciality_ids"),
            "joining_date": params.get("joining_date"),
            "sex": params.get("sex"),
            "degree_ids": params.get("degree_ids"),
            "doctor_fees": params.get("doctor_fees"),
            "doctor_department_id": params.get("doctor_department_id"),
            "registration_no": params.get("registration_no"),
            "total_experience": params.get("total_experience"),
            "working_institute": params.get("working_institute"),
            "work_location": params.get("work_location"),
            "doctor_description": params.get("doctor_description"),
            "sign_by": params.get("sign_by"),
            "email": params.get("email"),
            "mobile": params.get("mobile"),
            "doc_language": params.get("language"),
            "about_doctor": params.get("about_doctor"),
            "is_doctor": True,
            "state": "approve"
        }
        if not user_id:
            create_doctor = request.env['res.partner'].sudo().create(vals)
            values = {'partner_id': create_doctor.id,
                      'name': create_doctor.name,
                      'groups_id': request.env.ref('base.group_portal'),
                      'login': create_doctor.email,
                      }

            res = request.env['res.users'].sudo().create(values)
            create_doctor.user_id = res.id
            return {'type': 'success', 'message': " Doctor Created Successfully"}
        else:
            return {
                "type": "error", "message": "This Doctor is Alredy created"}

    def create_doctor_weeklyavailibility(self, params):
        """
            "method": create_doctor_weeklyavailibility,
            "params":
                "doctor_id",
                "available_weekdays",
                "from_time",
                "to_time",
                "totel_appointment",
        """
        doctor_id = request.env['res.partner'].sudo().search([('id', '=', params.get('doctor_id'))])

        from_time = request.env['time.hours'].sudo().search([('id', '=', params.get('from_time'))])

        to_time = request.env['time.hours'].sudo().search([('id', '=', params.get('to_time'))])
        if doctor_id:
            vals = {
                "doctor_id": doctor_id.id,
                'available_weekdays': params.get("available_weekdays"),
                'from_time': params.get("from_time"),
                "to_time": params.get("to_time"),
                "totel_appointment": params.get("totel_appointment"),
                "name": from_time.name + ' To ' + to_time.name
            }
            request.env['doctor.weeklyavalibility'].create(vals)
            return {
                "type": "success",
                "message": " create weekly availibility "
            }

    def doctor_information(self, params):
        """
            method: doctor_information
            params: {
                "login":"email"
            }
        """
        user_rec = request.env['res.users'].sudo().search(
            ['|', ('login', '=', params.get('login')), ('mobile', '=', params.get('login'))], limit=1,
            order='id ASC')
        if user_rec:
            return {
                "type": "success",
                "id": user_rec.id,
                "image_1920": image_data_uri(
                    user_rec.partner_id.image_1920) if user_rec.partner_id.image_1920 else False,
                "name": user_rec.partner_id.name,
                "speciality_ids": [(special.id, special.speciality) for special in user_rec.speciality_ids],
                "doctor_department_id": user_rec.partner_id.doctor_department_id.department,
                "joining_date": user_rec.partner_id.joining_date,
                "sex": user_rec.partner_id.sex,
                "degree_ids": [(deg.id, deg.degree) for deg in user_rec.degree_ids],
                "doctor_fees": user_rec.partner_id.doctor_fees,
                "registration_no": user_rec.partner_id.registration_no,
                "total_experience": user_rec.partner_id.total_experience,
                "working_institute": user_rec.partner_id.working_institute,
                "doctor_description": user_rec.partner_id.doctor_description,
                "email": user_rec.partner_id.email,
                "mobile": user_rec.partner_id.mobile,
                "sign_by": user_rec.partner_id.sign_by,
                "weekly_availibility_line": [{"id": weekly.id,
                                              "availabel_weekdays": [(days.id, days.name) for days in
                                                                     weekly.available_weekdays],
                                              "from_time": (weekly.from_time.id, weekly.from_time.name),
                                              "to_time": (weekly.from_time.id, weekly.from_time.time),
                                              "totel_appointment": weekly.totel_appointment,
                                              "total_time": weekly.name

                                              } for weekly in user_rec.weekly_avalibility_line]
            }
        else:
            return {"type": "error", "message": "no user found"}

    def patient_information(self, params):
        """
            method: patient_information
            params: {
                "login":"email"
            }
        """

        user_rec = request.env['res.users'].sudo().search(
            ['|', ('login', '=', params.get('login')), ('mobile', '=', params.get('login'))], limit=1,
            order='id ASC')
        if user_rec:
            return {
                "type": "success",
                "id": user_rec.id,
                "image": image_data_uri(user_rec.partner_id.image_1920) if user_rec.partner_id.image_1920 else False,
                "name": user_rec.partner_id.name,
                "date_of_birth": user_rec.partner_id.date_of_birth,
                "doctor_department_id": user_rec.partner_id.doctor_department_id.department,
                "age": user_rec.partner_id.age,
                "sex": user_rec.partner_id.sex,
                "marital_status": user_rec.partner_id.marital_status,
                "blood_group": user_rec.partner_id.blood_group,
                "doctor_id": user_rec.partner_id.doctor_id,
                "street": user_rec.partner_id.street,
                "street2": user_rec.partner_id.street2,
                "city": user_rec.partner_id.city,
                "state_id": user_rec.partner_id.state_id.name,
                "email": user_rec.partner_id.email,
                "mobile": user_rec.partner_id.mobile,
                "country_id": user_rec.partner_id.country_id.name,
                "confirmation_ref": user_rec.partner_id.confirmation_ref,

            }
        else:
            return {"type": "error", "message": "no user found"}

    def get_states(self, params):
        """
                method: "get_states"
                params: {}
            """
        state = [[(state.id, state.name), (state.country_id.id, state.country_id.name)] for state in
                 request.env['res.country.state'].sudo().search([])]
        return {
            'type': "success",
            'state': state
        }

    def get_countries(self, params):
        """
                method: "get_countries"
                params: {}
            """
        country = [[(country.id, country.name)] for country in request.env['res.country'].sudo().search([])]
        return {
            'type': "success",
            'country': country
        }

    def get_radiology(self, params):
        """
            method: get_radiology
            params: {}
        """
        radiology_info = [{
            "id": radio.id,
            "image": image_data_uri(radio.image) if radio.image else False,
            "radiologist_name_id": (radio.radiologist_name_id.name),
            "street": radio.street,
            "stree2": radio.street2,
            "city": radio.city,
            "state": (radio.state_id.id, radio.state_id.name),
            "country": (radio.country_id.id, radio.country_id.name),
            "website": radio.website,
            "phone": radio.phone,
            "mobile": radio.mobile,
            "email": radio.email,
        } for radio in request.env['radiology.radiology'].sudo().search([])]

        if radiology_info:
            return {
                "type": "success",
                "name": radiology_info
            }
        else:
            return {"type": "error", "message": "Not Found radiology"}

    def get_laboratory(self, params):
        """
            method: get_laboratory
            params: {}
        """

        laboratory_info = [{
            "id": laboratory.id,
            "image": image_data_uri(laboratory.image) if laboratory.image else False,
            "pathologist_id": (laboratory.pathologist_id.name),
            "street": laboratory.street,
            "stree2": laboratory.street2,
            "city": laboratory.city,
            "state": (laboratory.state_id.id, laboratory.state_id.name),
            "country": (laboratory.country_id.id, laboratory.country_id.name),
            "website": laboratory.website,
            "phone": laboratory.phone,
            "mobile": laboratory.mobile,
            "email": laboratory.email,
        } for laboratory in request.env['laboratory.laboratory'].sudo().search([])]

        if laboratory_info:
            return {
                "type": "success",
                "name": laboratory_info}
        else:
            return {"type": "error", "message": "Not Found Laboratory"}

    def get_degree(self, params):
        """
            method: get_degree
            params: {}
        """
        degree = [[(degree.id, degree.degree)] for degree in
                  request.env['doctor.degree'].sudo().search([])]

        if degree:
            return {
                "type": "success",
                "degree": degree
            }
        else:
            return {"type": "error", "message": "Not found Degree"}

    def get_depertment(self, params):
        """
            method: get_depertment
            params: {}
        """

        department = [[(depart.id, depart.department)] for depart in
                      request.env['doctor.department'].sudo().search([])]

        if department:
            return {
                "type": "success",
                "degree": department
            }
        else:
            return {"type": "error", "message": "Not found Department"}

    def get_speciality(self, params):
        """
            method: get_speciality
            params: {}
        """
        speciality = [[(special.id, special.speciality)] for special in
                      request.env['doctor.speciality'].sudo().search([])]

        if speciality:
            return {
                "type": "success",
                "degree": speciality
            }
        else:
            return {"type": "error", "message": "Not found Speciality"}

    def get_time_hours(self, params):
        """
            method: get_time_hours
            params: {}
        """
        time_hourse = [{
            "id": time_hours.id,
            "name": time_hours.name,
            "time": time_hours.time
        } for time_hours in
            request.env['time.hours'].sudo().search([])]

        if time_hourse:
            return {
                "type": "success",
                "name": time_hourse
            }
        else:
            return {"type": "error", "message": "Not Found Time"}

    def get_pharmacist_education(self, params):
        """
             method: get_pharmacist_education
             params: {}
         """

        pharma_education = [[(education.id, education.name)] for education in
                            request.env['pharmacist.education'].sudo().search([])]

        if pharma_education:
            return {
                "type": "success",
                "name": pharma_education
            }
        else:
            return {"type": "error", "message": "Not Found Pharmalist Education"}

    def get_pharmacist_information(self, params):
        """
             method: get_pharmacist_information
             params: {}
         """

        pharmacist_information = [{
            "id": education.id,
            "image": image_data_uri(education.image_1920) if education.image_1920 else False,
            "name": (education.pharmacist_education_ids.name),
            "street": education.street,
            "street2": education.street2,
            "city": education.city,
            "state_id": (education.state_id.id, education.state_id.name),
            "country_id": (education.country_id.id, education.country_id.name),
            "date_of_birth": education.date_of_birth,
            "age": education.age,
            "sex": education.sex
        } for education in
            request.env['res.partner'].sudo().search([('is_pharmacist', '=', True)])]

        if pharmacist_information:
            return {
                "type": "success",
                "name": pharmacist_information
            }
        else:
            return {"type": "error", "message": "Not Pharmacist Information"}

    def pharmacy_stock(self, params):
        """
             method: pharmacy_stock
             params: {}
         """
        pharmacy_stock = [{
            "id": product.id,
            "image": image_data_uri(product.image_1920) if product.image_1920 else False,
            "name": product.name,
            "lst_price": product.lst_price,
            "qty_available": product.qty_available
        } for product in
            request.env['product.product'].sudo().search([])]

        if pharmacy_stock:
            return {
                "type": "success",
                "name": pharmacy_stock
            }
        else:
            return {"type": "error", "message": "Not Found Pharmacy in medical"}

    def get_room_number(self, params):
        """
              method: get_room_number
              params: {}
          """
        room_number = [{
            "id": room.id,
            "room_details": room.room_details,
            "room_no": room.room_no,
            "state": room.state
        } for room in
            request.env['room'].sudo().search([])]

        if room_number:
            return {
                "type": "success",
                "name": room_number
            }
        else:
            return {"type": "error", "message": "not found Room Number in medical"}

    def get_room_facility(self, params):
        """
              method: get_room_facility
              params: {}
          """
        room = [[(
            room.id,
            room.name,
        )] for room in
            request.env['room.facilities'].sudo().search([])]

        if room:
            return {
                "type": "success",
                "name": room
            }
        else:
            return {"type": "error", "message": "not found Room medical"}

    def get_room_type(self, params):
        """
              method: get_room_type
              params: {}
          """
        room_type = [{
            "id": ro_type.id,
            "name": ro_type.name,
            "facility_ids": (ro_type.facility_ids.name),
            "room_no": ro_type.room_id.room_no,
            "price": ro_type.price
        } for ro_type in
            request.env['room.type'].sudo().search([])]

        if room_type:
            return {
                "type": "success",
                "name": room_type
            }
        else:
            return {"type": "error", "message": "Not found Room Type in medical"}

    def get_receptionist_information(self, params):
        """
              method: get_receptionist_information
              params: {}
          """
        receptionist_information = [{
            "id": info.id,
            "image": image_data_uri(info.image_1920) if info.image_1920 else False,
            "name": info.name,
            "sex": info.sex,
            "street": info.street,
            "street2": info.street2,
            "city": info.city,
            "state_id": (info.state_id.id, info.state_id.name),
            "country_id": (info.country_id.id, info.country_id.name),
            "state": info.state,
        } for info in
            request.env['res.partner'].sudo().search([('is_receptionist', '=', True)])]
        if receptionist_information:
            return {
                "type": "success",
                "name": receptionist_information
            }
        else:
            return {"type": "error", "message": "Not Found Receptionist Information in medical"}

    def get_radiologist_information(self, params):
        """
              method: get_radiologist_information
              params: {}
          """
        radiologist_information = [{
            "id": info.id,
            "image": image_data_uri(info.image_1920) if info.image_1920 else False,
            "name": info.name,
            "radiologist_education_ids": (info.radiologist_education_ids.name),
            "date_of_birth": info.date_of_birth,
            "age": info.age,
            "sex": info.sex,
            "street": info.street,
            "street2": info.street2,
            "city": info.city,
            "state_id": (info.state_id.id, info.state_id.name),
            "county_id": (info.country_id.id, info.country_id.name),
        } for info in
            request.env['res.partner'].sudo().search([('is_radiologist', '=', True)])]
        if radiologist_information:
            return {
                "type": "success",
                "name": radiologist_information
            }
        else:
            return {"type": "error", "message": "Not found Radiologist details"}

    def get_radiologist_education(self, params):
        """
               method: get_radiologist_education
               params: {}
           """
        radiologist_education = [[(education.id, education.name)] for education in
                                 request.env['radiologist.education'].sudo().search([])]

        if radiologist_education:
            return {
                "type": "success",
                "name": radiologist_education
            }
        else:
            return {"type": "error", "message": "Not found Radiologist Education details"}

    def get_radiology_test_type(self, params):
        """
               method: get_radiology_test_type
               params: {}
           """
        test_type = [[(test.id, test.test_name)] for test in
                     request.env['radio.test.type'].sudo().search([])]

        if test_type:
            return {
                "type": "success",
                "name": test_type
            }
        else:
            return {"type": "error", "message": "Not found Radiology Test Type details"}

    def get_radiology_test_price(self, params):
        """
               method: get_radiology_test_price
               params: {}
           """
        test_price = [{
            "id": test_price.id,
            "radio_name_name": test_price.radio_name_id.name,
            "select_state_id": test_price.select_test_id.test_name,
            "test_price": test_price.test_price

        } for test_price in
            request.env['radio.test.price'].sudo().search([])]

        if test_price:
            return {
                "type": "success",
                "name": test_price
            }
        else:
            return {"type": "error", "message": "Not found Radiology Test Price  details"}

    def get_pathologist_information(self, params):
        """
               method: get_pathologist_information
               params: {}
           """
        pathologist_information = [{
            "id": info.id,
            "image": image_data_uri(info.image_1920) if info.image_1920 else False,
            "name": info.name,
            "pathologist_education_ids": info.pathologist_education_ids.name,
            "date_of_birth": info.date_of_birth,
            "age": info.age,
            "sex": info.sex,
            "street": info.street,
            "street2": info.street2,
            "city": info.city,
            "state_id": (info.state_id.id, info.state_id.name),
            "country_id": (info.country_id.id, info.country_id.name),
        } for info in
            request.env['res.partner'].sudo().search([('is_pathologist', '=', True)])]
        if pathologist_information:
            return {
                "type": "success",
                "name": pathologist_information
            }
        else:
            return {"type": "error", "message": "Not found Pathologist details"}

    def get_pathologist_education(self, params):
        """
               method: get_pathologist_education
               params: {}
           """
        pathologist_education = [[(education.id, education.name)] for education in
                                 request.env['pathologist.education'].sudo().search([])]

        if pathologist_education:
            return {
                "type": "success",
                "name": pathologist_education
            }
        else:
            return {"type": "error", "message": "Not found Pathologist Education details"}

    def get_laboratory_test_type(self, params):
        """
               method: get_laboratory_test_type
               params: {}
           """
        test_type = [[(test.id, test.test_name)] for test in
                     request.env['lab.test.type'].sudo().search([])]

        if test_type:
            return {
                "type": "success",
                "name": test_type
            }
        else:
            return {"type": "error", "message": "Not found Pathology Test Type details"}

    def get_laboratory_test_price(self, params):
        """
               method: get_laboratory_test_price
               params: {}
           """
        test_price = [{
            "id": test_price.id,
            "name": test_price.lab_name_id.name,
            "select_test_id": test_price.select_test_id.test_name,
            "test_price": test_price.test_price,
            "state": test_price.state

        } for test_price in
            request.env['lab.test.price'].sudo().search([])]

        if test_price:
            return {
                "type": "success",
                "name": test_price
            }
        else:
            return {"type": "error", "message": "Not found Pathology Test Price  details"}

    def get_symptoms_type(self, params):
        """
                method: get_symptoms_type
                params: {}
            """
        sym_type = [[(
            symp.id,
            symp.type

        )] for symp in
            request.env['symptoms.type'].sudo().search([])]

        if sym_type:
            return {
                "type": "success",
                "name": sym_type
            }
        else:
            return {"type": "error", "message": "Not found Symptoms Type  details"}

    def get_symptoms_time(self, params):
        """
                method: get_symptoms_time
                params: {}
            """
        sym_time = [[(
            symp.id,
            symp.time

        )] for symp in
            request.env['symptoms.time'].sudo().search([])]

        if sym_time:
            return {
                "type": "success",
                "name": sym_time
            }
        else:
            return {"type": "error", "message": "Not found Symptoms Time  details"}

    def get_chief_complaint(self, params):
        """
                method: get_chief_complaint
                params: {}
            """
        chief_com = [[(
            chief.id,
            chief.name

        )] for chief in
            request.env['chief.complaints'].sudo().search([])]

        if chief_com:
            return {
                "type": "success",
                "name": chief_com
            }
        else:
            return {"type": "error", "message": "Not found Chief Complaints  details"}

    def get_local_examination(self, params):
        """
                method: get_local_examination
                params: {}
            """
        local_examination = [[(
            local.id,
            local.name

        )] for local in
            request.env['local.examination'].sudo().search([])]

        if local_examination:
            return {
                "type": "success",
                "name": local_examination
            }
        else:
            return {"type": "error", "message": "Not found Local Examination  details"}

    def get_system_examination(self, params):
        """
                method: get_system_examination
                params: {}
            """
        system_examination = [[(
            local.id,
            local.name

        )] for local in
            request.env['system.examination'].sudo().search([])]

        if system_examination:
            return {
                "type": "success",
                "name": system_examination
            }
        else:
            return {"type": "error", "message": "Not found System Examination  details"}

    def get_ipd_registration(self, params):
        """
                method: get_ipd_registration
                params: {}
            """
        ipd_registration = [{
            "id": ipd.id,
            "patient_id": ipd.patient_id.name,
            "doctor_id": ipd.doctor_id.name,
            "date_of_admit": ipd.date_of_admit,
            "select_room_type": ipd.select_room_type.name,
            "select_room_number": ipd.select_room_number.room_no,
            "attachment_ids": [(attach_file.id, attach_file.datas) for attach_file in ipd.attachment_ids],
            "state": ipd.state,
            "ipd_summery_line_ids": [{
                'id': line.id,
                "date_of_admit": line.date_of_admit,
                "disease_indication": line.disease_indication,
                "doctor_department_id": line.doctor_department_id.department,
                "doctor_refer_id": line.doctor_refer_id.name,
                "medicine_detail": line.medicine_detail.name,
            } for line in ipd.ipd_summary_line_ids]

        } for ipd in
            request.env['ipd.registration'].sudo().search([])]

        if ipd_registration:
            return {
                "type": "success",
                "name": ipd_registration
            }
        else:
            return {"type": "error", "message": "Not found Ipd Registration details"}

    def new_patient_book_appointment(self, params):
        """
            method: new_patient_book_appointment,
            params{
                "new_patient_name",
                "doctor_department_id",
                "street",
                "street2",
                "appointment_date",
                "country_id",
                "state_id",
                "city",
                "date_of_birth",
                "age",
                "sex",
                "blood_group",
                "mobile",
                "email",
                "doctor_id",
                "weekdays",
                "select_time_id"

            }
        """

        datetime_obj = datetime.strptime(params.get("appointment_date"), '%Y-%m-%d')
        date_obj = datetime_obj.date()
        vals = {
            'new_patient_name': params.get("new_patient_name"),
            'doctor_department_id': params.get("doctor_department_id"),
            'street': params.get('street'),
            'street2': params.get('street2'),
            'appointment_date': date_obj,
            'country_id': params.get('country_id'),
            'state_id': params.get('state_id'),
            'city': params.get('city'),
            'date_of_birth': params.get('date_of_birth'),
            'age': params.get('age'),
            'sex': params.get('sex'),
            'blood_group': params.get('blood_group'),
            'mobile': params.get('mobile'),
            'email': params.get('email'),
            'doctor_id': params.get("doctor_id"),
            'is_normal_opd': True,
            'weekdays': params.get('weekdays'),
            'select_time_id': params.get('select_time_id'),
        }

        patient_id = request.env['res.partner'].sudo().search([('email', '=', params.get('email'))])
        if not patient_id:
            create_opd = request.env['opd.opd'].sudo().create(vals)
            create_opd.sudo().create_new_patient()
            return {
                "type": 'success',
                "message": "Created Opd Successfully"
            }
        else:
            return {"type": "error", "message": "This username has been created by  already patient"}

    def get_available_weekdays(self, params):
        """
           method: get_available_weekdays
           params: {
                "id":"doctor_id"
           }
       """
        weekdays_id = request.env['doctor.weeklyavalibility'].sudo().search(
            [('doctor_id.id', '=', params.get('id'))],
            order='id ASC')

        if weekdays_id:
            weekly_availibility = [{"id": weekly.id,
                                    "availabel_weekdays": [(days.id, days.name) for days in
                                                           weekly.available_weekdays]
                                    } for weekly in weekdays_id]
            return {"type": "success", "weekly_availibility_line": weekly_availibility}
        else:
            return {
                'type': 'error',
                'message': "please enter valid doctor id "
            }

    def get_doctor_select_time(self, params):
        """
           method: get_doctor_select_time
           params: {}
       """
        weekdays_id = request.env['doctor.weeklyavalibility'].sudo().search(
            [('doctor_id.id', '=', params.get('id'))],
            order='id ASC')
        if weekdays_id:
            return {
                'type': 'success',
                'select_time_id': [(time.id, time.name) for time in weekdays_id]
            }
        else:
            return {"type": "error", "message": "Please Enter valid Doctor id "}

    def old_patient_book_appointment(self, params):
        """
            "method": old_patient_book_appointment
            "params"{
                "patient_id",
                "doctor_department_id",
                "doctor_id",
                "appointment_date",
                "weekdays",
                "select_time_id",
            }
        """

        patient_id = request.env['res.partner'].sudo().search(
            [('confirmation_ref', '=', params.get('confirmation_ref'))])
        values = {
            "patient_id": patient_id.id,
            "doctor_department_id": params.get("doctor_department_id"),
            "doctor_id": params.get("doctor_id"),
            "appointment_date": params.get("appointment_date"),
            "weekdays": params.get("weekdays"),
            "select_time_id": params.get('select_time_id'),
            "is_normal_opd": True,
            "state": 'pending',
            "existing_patient_name": True
        }
        if patient_id:
            create_opd = request.env['opd.opd'].sudo().create(values)
            return {
                "type": 'success',
                "message": "created successfully opd"
            }
        else:
            return {"type": "error", "message": "not create opd"}

    def appointment_patient_details(self, params):
        """
           method: appointment_patient_details
           params: {
                "login":"email"
           }
       """
        user_rec = request.env['res.users'].sudo().search(
            ['|', ('login', '=', params.get('login')), ('mobile', '=', params.get('login'))], limit=1,
            order='id ASC')
        if user_rec:
            opd_id = request.env['opd.opd'].sudo().search(
                [('patient_id.user_id', '=', user_rec.id), ('is_normal_opd', '=', True)])
            #  Appointment(opd) details get from patient form
            if opd_id:
                opd = [{
                    'id': opds.id,
                    'patient_name': (opds.patient_id.name, opds.name),
                    'doctor_department_id': opds.doctor_department_id.department,
                    'doctor_id': opds.doctor_id.name,
                    'appointment_date': opds.appointment_date,
                    'weekdays': opds.weekdays,
                    'select_time_id': opds.select_time_id.name,
                    'symptoms_line_id': [{
                        "symptoms_type": [(sym.id, sym.type) for sym in symptoms.symptoms_id],
                        "symptoms_time": [(time.id, time.time) for time in symptoms.symptoms_time_id],
                    } for symptoms in opds.symptoms_line_id],
                    'medicine_line_id': [{
                        "id": medicine.id,
                        "prescriptionDate": medicine.prescriptionDate,
                        "pharmacy_id": medicine.pharmacy_id.name,
                        "indication_id": medicine.indication_id.name,
                        "medicine_id": [(med.name) for med in medicine.medicine_id],
                        "morning_dose": medicine.morning_dose,
                        "noon_dose": medicine.noon_dose,
                        "evening_dose": medicine.evening_dose,
                        "night_dose": medicine.night_dose,
                        "dose": medicine.dose,
                        # "after_before_meal": medicine.after_before_meal,
                        "frequency": medicine.frequency,
                        "note": medicine.note,
                        "medicine_days": medicine.medicine_days,
                        "total_tablets": medicine.total_tablets,
                        "attachment_ids": medicine.attachment_ids,
                    } for medicine in opds.medicine_line_ids],
                    'lab_line_ids': [{
                        "id": lab_id.id,
                        "prescriptionDate": lab_id.prescriptionDate,
                        "laboratory_id": (lab_id.id, lab_id.laboratory_id.name),
                        "laboratory_test_id": [(lab.id, lab.test_name) for lab in lab_id.laboratory_test_id],
                        "note": lab_id.note,
                        "attachment_ids": lab_id.attachment_ids
                    } for lab_id in opds.lab_line_ids],

                    'radio_line_ids': [{
                        "id": radio_line.id,
                        "prescriptionDate": radio_line.prescriptionDate,
                        "radiology_id": (radio_line.id, radio_line.radiology_id.name),
                        "radiology_test_id": [(radio.id, radio.test_name) for radio in radio_line.radiology_test_id],
                        "note": radio_line.note,
                        "attachment_ids": radio_line.attachment_ids
                    } for radio_line in opds.radio_line_ids],
                    "follow_up_date": opds.follow_up_date,
                    "followup_advice": opds.followup_advice,

                } for opds in opd_id]
                return {
                    'type': "success",
                    'opd_details': opd
                }
            else:
                return {'type': "error", "message": "Not Found Opd For Login Patient"}
        else:
            return {'type': "error", "message": " Please Enter Valid Username "}
