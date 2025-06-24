from odoo import fields, models, api, _


class productproduct(models.Model):
    _inherit = 'product.product'

    is_medicine = fields.Boolean('Is medicine')
    content = fields.Char('Content')

    manufacturing_date = fields.Date("Manufacturing Date")
    expiry_date = fields.Date("Expiry Date")


class PharmacyPrescription(models.Model):
    _name = "pharmacy.prescription"
    _description = "pharmacy prescription Details"

    @api.model  # seq
    def create(self, vals):
        res = super(PharmacyPrescription, self).create(vals)
        vals['name'] = self.env['ir.sequence'].next_by_code('PharmacyPrescription')
        res.name = vals['name']
        return res

    @api.onchange('opd_id')
    def onchange_name(self):
        for i in self:
            i.patient_id = i.opd_id.patient_id.id
            i.prescriptionDate = i.opd_id.appointment_date
            i.doctor_id = i.opd_id.doctor_id.id

    def confirm_prescription(self):
        self.state = 'done'
        return {
            'name': _('Update quantity on hand'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('cr_medical_base.view_update_pharmacy_stock').id,
            'res_model': 'update.pharmacy.stock',
            'target': 'new',
            'context': {'medicine_ids': self.env.context.get('medicine_id', self.medicine_id).ids}
        }

    def cancel_prescription(self):
        self.state = 'cancel'

    name = fields.Char(string="seq")
    pharmacy_id = fields.Many2one("pharmacy.pharmacy", string="Pharmacy Name")
    patient_id = fields.Many2one("res.partner", string="Patient Name")
    doctor_id = fields.Many2one("res.partner", string="Doctor Name")
    prescriptionDate = fields.Date(string="Date", default=fields.Date.today())
    opd_id = fields.Many2one('opd.opd')
    medicine_days = fields.Integer("Days/Quantity")
    total_tablets = fields.Float(string="Total Tablets")
    # medicine_id = fields.Many2many("product.product", string="Medicine Name", domain="[('is_medicine','=',True)]")
    medicine_id = fields.Many2one("product.product", string="Medicine Name", domain="[('is_medicine','=',True)]")
    indication_id = fields.Many2one("disease.description", string="Indication")
    morning_dose = fields.Boolean(string="Morning")
    noon_dose = fields.Boolean(string="Noon")
    evening_dose = fields.Boolean(string="Evening")
    night_dose = fields.Boolean(string="Night")
    # after_before_meal = fields.Boolean(string="A/B meal")
    frequency = fields.Selection([('after meal', 'After Meal'), ('before meal', 'Before Meal')], default='after meal',
                                 string="Frequency")
    dose = fields.Integer(string="Dose")
    attachment_ids = fields.Many2many('ir.attachment')
    note = fields.Char("Notes")
    state = fields.Selection([('done', 'Done'), ('cancel', 'Cancel')])
    ref_opd_id = fields.Many2one('opd.opd')
    price = fields.Float(string="Unit Price", readonly="1")
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', ondelete="restrict")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)

    @api.onchange('medicine_days', 'dose', 'morning_dose', 'noon_dose', 'evening_dose', 'night_dose')
    def onchange_medicine_days(self):
        total_medicine = 0
        if self.morning_dose:
            total_medicine += 1
        if self.noon_dose:
            total_medicine += 1
        if self.evening_dose:
            total_medicine += 1
        if self.night_dose:
            total_medicine += 1
        if self.medicine_days:
            self.total_tablets = self.dose * self.medicine_days * total_medicine
        if self.dose:
            self.total_tablets = self.dose * self.medicine_days * total_medicine

    def read_converted(self):
        field_names = ["medicine_id", "name", "total_tablets"]
        results = []
        for medicine_line in self:
            item = medicine_line.read(field_names)[0]
            results.append(item)
            item['total_tablets'] = self._convert_qty(medicine_line, item['total_tablets'], 's2p')
            results.append(item)
        return results

    @api.model
    def _convert_qty(self, medicine_line, qty, direction):

        product_uom = medicine_line.medicine_id.uom_id
        sale_line_uom = medicine_line.product_uom
        if direction == 's2p':
            return sale_line_uom._compute_quantity(qty, product_uom, False)


class patientDisease(models.Model):
    _name = "disease.description"
    _description = "About patient Disease"

    name = fields.Char("Indication")


class medicineForm(models.Model):
    _name = "medicine.from"
    _description = "About medicine From Description(Capsule...etc)"

    name = fields.Char(string="Form")
