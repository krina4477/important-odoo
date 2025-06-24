# -*- encoding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

from odoo import models, fields, api


class RadiologyPrescription(models.Model):
    _inherit = "radiology.prescription"
    _description = "radiology prescription Details"

    radiology_id = fields.Many2one("radiology.radiology", string="Radiology Name")


class Radiology(models.Model):
    _name = 'radiology.radiology'
    _description = 'Information About Radiology'

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
        tree_view_id = self.env.ref('cr_medical_base.cr_radiology_prescription_tree_view').id
        form_view_id = self.env.ref('cr_medical_base.cr_radiology_prescription_form_view').id
        return {
            'name': 'Prescription List',
            'type': 'ir.actions.act_window',
            'res_model': 'radiology.prescription',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('radiology_id', '=', self.id)],
            'res_id': False,
            'target': 'current',

        }

    # @api.one
    def compute_count_prescription(self):
        for i in self:
            a = self.env['radiology.prescription'].search([('radiology_id', '=', i.id)])
            i.prescription_count = len(a.ids)

    image = fields.Binary("image")
    name = fields.Char("name")
    radiologist_name_id = fields.Many2one("res.partner", "Radiologist Name")
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
    radiology_lines = fields.Char()
    info = fields.Text()


class RadioTestType(models.Model):
    _inherit = 'radio.test.type'
    _description = 'Type of Test Available In Radiology'

    test_name = fields.Char("Test", required=True)


class RadioTestPrice(models.Model):
    _name = 'radio.test.price'
    _description = 'Set The Price Of The Specific Test'
    _rec_name = 'select_test_id'

    def confirm_state(self):
        self.state = "confirm"

    select_test_id = fields.Many2one('radio.test.type', string='Select Test', required=True)
    test_price = fields.Integer(string='Test Price', required=True)
    radio_name_id = fields.Many2one('radiology.radiology', string='Radiology Name')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], default='draft')


class PatientRadioTest(models.Model):
    _name = 'patient.radio.test'
    _description = 'Patient Can See The Radiology Details'
    _rec_name = "select_test_id"

    @api.onchange('select_test_id')
    def _onchange_test_price(self):
        if self.select_test_id:
            test_id = self.env['radio.test.price'].search([('select_test_id', '=', self.select_test_id.id)])
            self.test_price = test_id.test_price

    radio_detail_id = fields.Many2one('radiology.radiology', string='Radiology Name', required=True)
    patient_id = fields.Many2one("res.partner", required=True)
    select_test_id = fields.Many2one('radio.test.price', string='Select Test', required=True)
    test_price = fields.Integer('Test Price', required=True)
