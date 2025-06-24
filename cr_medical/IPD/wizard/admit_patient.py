# -*- coding: utf-8 -*-
from odoo import models, fields


class AdmitPatient(models.TransientModel):
    _name = 'admit.patient'
    _description = "Admit Patient From Wizard"

    date_of_admit = fields.Date(string="Admit Date")
    room_type_id = fields.Many2one('room.type', string='Room Type')
    room_id = fields.Many2one('room', string='Room Number')
    bed_id = fields.Many2one('bed.bed', string='Bed')

    def admit_patient(self):
        active_id = self.env['opd.opd'].sudo().browse(self._context.get('active_id'))
        active_id.state = 'admitted'
        if not active_id.opd_id:
            opd_id = active_id.id
        else:
            opd_id = active_id.opd_id.id
        for rec in self:
            values = {
                'opd_id': active_id.id,
                'ref_opd_id': opd_id,
                'patient_id': active_id.patient_id.id or active_id.new_patient_id.id,
                'doctor_department_id': active_id.doctor_department_id.id,
                'doctor_id': active_id.doctor_id.id,
                'date_of_admit': active_id.appointment_date,
                'select_room_type': rec.room_type_id.id,
                'select_room_number': rec.room_id.id,
                'bed_id': rec.bed_id.id,
            }
            created_ipd_registration = self.env['ipd.registration'].create(values)
            action = {
                'name': "IPD Registration",
                'type': 'ir.actions.act_window',
                'res_model': 'ipd.registration',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('IPD.cr_ipd_registration_form_view').id,
                'res_id': created_ipd_registration.id,
            }
            return action

# class Room(models.Model):
#     _name = "room"
#     _description = "room"
#
#     room_type_id = fields.Many2one("room.type", string="Room Type")
#     state = fields.Selection(
#         [('draft', 'Draft'), ('selected', 'Selected'), ("not selected", "Not Selected")],
#         string="Room Number", default='not selected')
#
#
# class RoomType(models.Model):
#     _name = "room.type"
#     _description = "room type"
#
#     name = fields.Char(string='Room Type', required=True)
