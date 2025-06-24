from odoo import fields, models, api, _
from datetime import date


class RadiologyPrescription(models.Model):
    _name = "radiology.prescription"
    _description = "radiology prescription Details"

    @api.model  # seq
    def create(self, vals):
        res = super(RadiologyPrescription, self).create(vals)
        vals['name'] = self.env['ir.sequence'].next_by_code('RadiologyPrescription')
        res.name = vals['name']
        return res

    @api.onchange('opd_id')
    def onchange_name(self):
        for i in self:
            i.patient_id = i.opd_id.patient_id.id
            i.prescriptionDate = i.opd_id.appointment_date
            i.doctor_id = i.opd_id.doctor_id.id

    name = fields.Char(string="seq")
    radiology_id = fields.Many2one("radiology.radiology", string="Radiology Name")
    patient_id = fields.Many2one("res.partner", string="Patient Name")
    doctor_id = fields.Many2one("res.partner", string="Doctor Name")
    prescriptionDate = fields.Date(string="Date", default=fields.Date.today())
    opd_id = fields.Many2one('opd.opd')
    radiology_test_id = fields.Many2many("radio.test.type", string="Radio Test Name")
    attachment_ids = fields.Many2many('ir.attachment')
    note = fields.Char("Notes")
    state = fields.Selection([('done', 'Done'), ('cancel', 'Cancel')])
    ref_opd_id = fields.Many2one('opd.opd')
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)


    def confirm_prescription(self):
        self.state = 'done'

    def cancel_prescription(self):
        self.state = 'cancel'


class RadioTestType(models.Model):
    _name = 'radio.test.type'
    _description = 'Type of Test Available In Radiology'
    _rec_name = 'test_name'

    test_name = fields.Char("Test", required=True)
