from odoo import fields, models, api
from datetime import date


class LaboratoryPrescription(models.Model):
    _name = "laboratory.prescription"
    _description = "laboratory prescription Details"

    @api.model  # seq
    def create(self, vals):
        res = super(LaboratoryPrescription, self).create(vals)
        vals['name'] = self.env['ir.sequence'].next_by_code('LaboratoryPrescription')
        res.name = vals['name']
        return res

    @api.onchange('opd_id')
    def onchange_name(self):
        for i in self:
            i.patient_id = i.opd_id.patient_id.id
            i.prescriptionDate = i.opd_id.appointment_date
            i.doctor_id = i.opd_id.doctor_id.id

    name = fields.Char(string="seq")
    laboratory_id = fields.Many2one("laboratory.laboratory", string="Laboratory Name")
    patient_id = fields.Many2one("res.partner", string="Patient Name")
    doctor_id = fields.Many2one("res.partner", string="Doctor Name")
    prescriptionDate = fields.Date(string="Date", default=fields.Date.today())
    opd_id = fields.Many2one('opd.opd')
    ref_opd_id = fields.Many2one('opd.opd')
    laboratory_test_id = fields.Many2many("lab.test.type", string="Lab Test Name")
    attachment_ids = fields.Many2many('ir.attachment')
    note = fields.Char("Notes")
    state = fields.Selection([('done', 'Done'), ('cancel', 'Cancel')])
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)


    def confirm_prescription(self):
        self.state = 'done'

    def cancel_prescription(self):
        self.state = 'cancel'


class LabTestType(models.Model):
    _name = 'lab.test.type'
    _description = 'Type of Test Available In Laboratory'
    _rec_name = 'test_name'

    test_name = fields.Char("Test", required=True)
