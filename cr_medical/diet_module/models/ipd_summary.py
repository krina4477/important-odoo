from odoo import models, fields


class IpdSummary(models.Model):
    _inherit = "ipd.summary"

    # open wizard on diet button
    def get_diet(self):
        context = {
            'default_patient_id': self.ipd_id.patient_id.id if self.ipd_id and self.ipd_id.patient_id else False,
            'default_date_of_admit': self.date_of_admit,  # set default date of admit in wizard
            'default_department': self.ipd_id.doctor_department_id.id if self.ipd_id and self.ipd_id.doctor_department_id else False,
        }
        return {
            "name": "Set Diet Plan",
            "type": "ir.actions.act_window",
            "res_model": "diet.plan",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }
