# -*- encoding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class PharmacyPrescription(models.Model):
    _inherit = "pharmacy.prescription"
    _description = "pharmacy prescription Details"

    pharmacy_id = fields.Many2one("pharmacy.pharmacy", string="Pharmacy Name")


class pharmacy(models.Model):
    _name = 'pharmacy.pharmacy'
    _description = 'Information About pharmacy'

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    def toggle_prescription_list(self):
        tree_view_id = self.env.ref('pharmacy.inherited_cr_pharmacy_prescription_tree_view').id
        form_view_id = self.env.ref('pharmacy.inherited_cr_pharmacy_prescription_form_view').id
        return {
            'name': 'Prescription List',
            'type': 'ir.actions.act_window',
            'res_model': 'pharmacy.prescription',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('pharmacy_id', '=', self.id)],
            'res_id': False,
            'target': 'current',

        }

    def compute_count_prescription(self):
        for i in self:
            a = self.env['pharmacy.prescription'].search([('pharmacy_id', '=', i.id)])
            i.prescription_count = len(a.ids)

    image = fields.Binary("image")
    name = fields.Char("name")
    pharmacist_name_id = fields.Many2one("res.partner", "Pharmacist name")
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
    pharmacy_lines = fields.Char()
    info = fields.Text()


class StockQuant(models.Model):
    _inherit = "stock.quant"
    _description = 'Information About stock'

    @api.model
    def _get_inventory_fields_write(self):
        fields = ['inventory_quantity', 'inventory_quantity_auto_apply', 'inventory_diff_quantity',
                  'inventory_date', 'user_id', 'inventory_quantity_set', 'is_outdated', 'product_id']
        return fields
