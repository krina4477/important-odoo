from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class ReportWizard(models.TransientModel):
    _name = "medicine.report"
    _description = "medicine report"

    start_date = fields.Datetime('Start date')
    end_date = fields.Datetime('End date')

    def button_export_pdf(self):
        medicine_stock = self.env['product.product'].search([('is_medicine', '=', True)])
        for stock in medicine_stock:
            print('++++++++stock', stock)
        if self.start_date and self.end_date:
            opd_id = self.env['opd.opd'].search(
                [('medicine_line_ids.prescriptionDate', '>=', self.start_date),
                 ('medicine_line_ids.prescriptionDate', '<=', self.end_date)])

            for rec in opd_id:
                for medicine in rec.medicine_line_ids:
                    print("++++++++++++opd_id++++++++", medicine.total_tablets)

        # --------------------------Medicine Stock Report ----------------------------

        if self.start_date and self.end_date:
            user_date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
            medicine_list = []
            for medicine in medicine_stock:
                vals = {
                    'name': medicine.name,
                    'expiry_note': medicine.expiry_note,
                    'manufacturing_date': medicine.manufacturing_date,
                    'expiry_date': medicine.expiry_date,
                    'lst_price': medicine.lst_price,
                    'standard_price': medicine.standard_price,
                    'qty_available': medicine.qty_available,
                    'virtual_available': medicine.virtual_available,
                }
                medicine_list.append(vals)
            data = {
                'start_date': self.start_date.strftime(user_date_format),
                'end_date': self.end_date.strftime(user_date_format),
                'search_record': medicine_list
            }
            return self.env.ref('cr_medical_base.action_medicine_stock_reports').report_action(self, data=data)
