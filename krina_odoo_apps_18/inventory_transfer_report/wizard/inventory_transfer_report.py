from odoo import fields, models, api, _
from odoo.exceptions import UserError
import base64
from io import BytesIO
import xlsxwriter
from odoo import models
from odoo.http import content_disposition
from odoo.tools.misc import xlsxwriter
import io
from datetime import datetime


class InventoryTransferReport(models.TransientModel):
    _name = "report.inventory.transfer"
    _description = "inventory transfer report"

    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    report_name = fields.Selection([
                    ('transfer_by_details', 'Transfer by Detail'),
                    ('transfer_in', 'Transfer In'),
                    ('transfer_out', 'Transfer Out')
                ], default="transfer_by_details")
    location_id = fields.Many2one('stock.location', 'Source Location')
    location_dest_id = fields.Many2one('stock.location', string="Destination Location")
    # company_id = fields.Many2one('res.company', string='Company', required=True)
    company_ids = fields.Many2many('res.company', string='Companies', required=True, domain=lambda self: [('id', 'in', self.env.user.company_ids.ids)])
    print_out = fields.Selection([
                    ('pdf', 'PDF'),
                    ('xlsx', 'XLSX')
                ], string="Output Format", required=True)

    def print_pdf_xlsx(self):
        self.ensure_one()

        # PDF output
        if self.print_out == 'pdf':
            return self.env.ref('inventory_transfer_report.action_transfer_pdf_report').report_action(self)

        # XLSX output
        elif self.print_out == 'xlsx':
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})

            # Formats
            title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14})
            subtitle_format = workbook.add_format({'align': 'center'})
            header_format = workbook.add_format({
                'bold': True, 'align': 'center', 'valign': 'vcenter',
                'border': 1, 'bg_color': '#D9D9D9'
            })
            normal = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
            # company_name = self.company_id.name if self.company_id else "Unknown Company"
            company_name = self.company_ids[0].name if self.company_ids else "Unknown Company"
            sheet = workbook.add_worksheet(company_name[:31])
            sheet.merge_range('A1:N1', f'Company : {company_name}', title_format)
            sheet.merge_range('A2:N2', f'From {self.start_date} to {self.end_date}', subtitle_format)

            headers = ['No', 'Original Store', 'Transfer No.','Transfer Date', 'Destination Store', 'Product ID', 'Barcode', 'Description', 'Qty', 'Cost By Unit', 'Amount']
            column_widths = [5, 12, 15, 15, 18, 15, 12, 15, 10, 25, 25, 10, 15]
            header_row = 2

            for col, (header, width) in enumerate(zip(headers, column_widths)):
                sheet.write(header_row, col, header, header_format)
                sheet.set_column(col, col, width)

            for row in range(header_row + 1, header_row + 6):
                for col in range(len(headers)):
                    sheet.write(row, col, '', normal)

            workbook.close()
            output.seek(0)
            xls_data = output.read()

            filename = f'Inventory_Transfer_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            file_data = base64.b64encode(output.getvalue())

            attachment = self.env['ir.attachment'].create({
                'name': filename,
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

            # output = io.BytesIO()
            # workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            # worksheet = workbook.add_worksheet('Inventory Transfer Report')
            #
            # bold_format = workbook.add_format({'bold': True})
            #
            # headers = [
            #     'Start Date', 'End Date', 'Report Type', 'Source Location',
            #     'Destination Location', 'Company'
            # ]
            # values = [
            #     str(self.start_date or ''),
            #     str(self.end_date or ''),
            #     dict(self._fields['report_name']._description_selection(self.env)).get(self.report_name, ''),
            #     self.location_id.display_name or '',
            #     self.location_dest_id.display_name or '',
            #     self.company_id.name or ''
            # ]
            #
            # for col_num, (header, value) in enumerate(zip(headers, values)):
            #     worksheet.write(0, col_num, header, bold_format)
            #     worksheet.write(1, col_num, value)
            #
            #     # Adjust column width to fit the longest of header or value
            #     max_length = max(len(header), len(value))
            #     worksheet.set_column(col_num, col_num, max_length + 2)
            #
            # workbook.close()
            # file_data = base64.b64encode(output.getvalue())
            # attachment = self.env['ir.attachment'].create({
            #     'name': 'inventory_transfer_report.xlsx',
            #     'type': 'binary',
            #     'datas': file_data,
            #     'res_model': self._name,
            #     'res_id': self.id,
            #     'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            # })
            #
            # return {
            #     'type': 'ir.actions.act_url',
            #     'url': '/web/content/%s?download=true' % attachment.id,
            #     'target': 'self',
            # }
