from odoo import models, fields, api


class DietPlan(models.TransientModel):
    _name = "diet.plan"
    _description = "Diet"

    break_fast_ids = fields.Many2many("break.fast", string="Breakfast", required=True)
    lunch_ids = fields.Many2many("lunch.info", string="Lunch")
    dinner_ids = fields.Many2many("dinner.info", string="Dinner")
    patient_id = fields.Many2one('res.partner', string='Patient Name')
    date_of_admit = fields.Date("Admit Date", default=lambda self: self._default_date_of_admit())
    ipd_id = fields.Many2one("ipd.registration")
    doctor_department_id = fields.Many2one('doctor.department', string="Doctor Department")

    def set_diet(self):
        kitchen_details_obj = self.env["kitchen.details"]

        for rec in self:
            # Create a new record in the kitchen.details model for each DietPlan
            kitchen_details_obj.create({
                "break_fast_ids": [(6, 0, rec.break_fast_ids.ids)],
                "lunch_ids": [(6, 0, rec.lunch_ids.ids)],
                "dinner_ids": [(6, 0, rec.dinner_ids.ids)],
                "patient_id": rec.patient_id.id,  # Set the patient_id in kitchen.details
                "date_of_admit": rec.date_of_admit,  # Set the date_of_admit in kitchen.details
                "doctor_department_id": rec.doctor_department_id.id,  # Set the doctor_department_id in kitchen.details
            })

    def _default_patient(self):
        return self.env['res.partner'].browse(
            self.env.context.get('default_patient_id')).display_name if self.env.context.get(
            'default_patient_id') else False

    def _default_date_of_admit(self):
        return self.env.context.get('default_date_of_admit', False)

    @api.model
    def default_get(self, fields_list):
        defaults = super(DietPlan, self).default_get(fields_list)

        # Get the default department from the context
        default_department_id = self.env.context.get('default_department')
        if default_department_id:
            defaults['doctor_department_id'] = default_department_id

        return defaults
