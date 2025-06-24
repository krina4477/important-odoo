# -*- coding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import api, exceptions, fields, models


class LaboratoryPrescription(models.Model):
    _inherit = "laboratory.prescription"
    _description = "laboratory prescription Details"

    laboratory_id = fields.Many2one("laboratory.laboratory", string="Laboratory Name")


class Laboratory(models.Model):
    _name = "laboratory.laboratory"
    _description = "laboratory prescription Details"

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    # @api.multi
    def toggle_prescription_list(self):
        tree_view_id = self.env.ref('cr_medical_base.cr_laboratory_prescription_tree_view').id
        form_view_id = self.env.ref('cr_medical_base.cr_laboratory_prescription_form_view').id
        return {
            'name': 'Prescription List',
            'type': 'ir.actions.act_window',
            'res_model': 'laboratory.prescription',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('laboratory_id', '=', self.id)],
            'res_id': False,
            'target': 'current',

        }

    # @api.one
    def compute_count_prescription(self):
        for i in self:
            a = self.env['laboratory.prescription'].search([('laboratory_id', '=', i.id)])
            i.prescription_count = len(a.ids)

    image = fields.Binary("image")
    name = fields.Char("name")
    pathologist_id = fields.Many2one("res.partner", "Tab Technician Name")
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    city = fields.Char("City")
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    website = fields.Char("Website")
    phone = fields.Char("Phone")
    mobile = fields.Char("mobile")
    email = fields.Char("Email")
    prescription_count = fields.Char(compute='compute_count_prescription')
    laboratory_lines = fields.Char()
    info = fields.Text()


class LabTestType(models.Model):
    _inherit = 'lab.test.type'

    test_name = fields.Char("Test")


class LabTestPrice(models.Model):
    _name = 'lab.test.price'
    _description = 'Set The Price Of The Specific Test'
    _rec_name = 'select_test_id'

    def confirm_state(self):
        self.state = "confirm"

    select_test_id = fields.Many2one('lab.test.type', string='Select Test', required=True)
    test_price = fields.Integer(string='Test Price', required=True)
    lab_name_id = fields.Many2one('laboratory.laboratory', string='Laboratory Name', required=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], default='draft')


class PatientLabTest(models.Model):
    _name = 'patient.lab.test'
    _description = 'Patient Can See The Laboratory Details'
    _rec_name = "select_test_id"

    lab_detail_id = fields.Many2one('laboratory.laboratory', string='Laboratory Name', required=True)
    patient_id = fields.Many2one("res.partner", required=True)
    select_test_id = fields.Many2one('lab.test.price', string='Select Test', required=True)
    test_price = fields.Integer('Test Price', required=True)

    @api.onchange('select_test_id')
    def _onchange_test_price(self):
        if self.select_test_id:
            test_id = self.env['lab.test.price'].search([('select_test_id', '=', self.select_test_id.id)])
            self.test_price = test_id.test_price
