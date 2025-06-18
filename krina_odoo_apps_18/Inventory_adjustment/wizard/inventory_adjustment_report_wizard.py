from odoo import models, fields, api
import io
import xlsxwriter
from odoo.http import request
import base64



class InventoryAdjustmentWizard(models.TransientModel):
     _name = 'inventory.adjustment.report.wizard'
     _description = "Inventory Adjustment Report Wizard"

     start_date = fields.Date('Start Date', required=True)
     end_date = fields.Date('End Date', required=True)
     group_by = fields.Selection([('article', 'Article'),
                                  ('criteria', 'Criteria')], 'Group By', default='article', required=True)
     report_type_1= fields.Selection([('detail', 'Detail'),
                                     ('summary', 'Summary'),
                                     ], 'Report Type')
     report_type_2 = fields.Selection([('1', '1 = by Division'),
                                     ('2', '2 = by Department'),
                                     ('3', '3 = by Sub Department'),
                                     ('4', '4 = by Division and Article Sorted'),
                                     ('5', '5 = by Department and Article Sorted'),
                                     ('6', '6 = by Sub Department and Article Sorted'),
                                     ('7', '2 = by Department and Supplier'),
                                     ('8', '2 = by Store'),
                                     ], 'Report Type')
     branch = fields.Char('Branch', required=True)
     company_id = fields.Many2one('res.company', string="Company", required=True)
     print_out = fields.Selection([('xls', 'XLS'), ('pdf', 'PDF')], 'Print Out', required=True)

     @api.onchange('group_by')
     def _onchange_group_by(self):
          if self.group_by == 'article':
               self.report_type_1 = 'detail'
          elif self.group_by == 'criteria':
               self.report_type_2 = '1'

     def generate_xls(self):
          output = io.BytesIO()

          workbook = xlsxwriter.Workbook(output, {'in_memory': True})
          worksheet = workbook.add_worksheet('Inventory Excel Report')
          # worksheet.write(0, 0, 'Header 1')
          workbook.close()
          file_data = base64.b64encode(output.getvalue())
          attachment = self.env['ir.attachment'].create({
               'name': 'empty_inventory_excel_report.xlsx',
               'type': 'binary',
               'datas': file_data,
               'res_model': self._name,
               'res_id': self.id,
               'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          })

          return {
               'type': 'ir.actions.act_url',
               'url': '/web/content/%s?download=true' % attachment.id,
               'target': 'self',
          }

     def generate_pdf(self):
          data = {
               'model_id': self.id,
               'form': self.env.context
          }
          return self.env.ref('Inventory_adjustment.action_report_Pdf').report_action(None, data=data)

     def action_print_reports(self):
          if self.print_out == 'xls':
               return self.generate_xls()
          if self.print_out == 'pdf':
               return self.generate_pdf()
