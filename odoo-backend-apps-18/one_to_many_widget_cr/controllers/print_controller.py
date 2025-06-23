# -*- encoding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import base64
import json
import io
from odoo import http
from odoo.tools.misc import xlsxwriter

class ExcelExport(http.Controller):

    def from_data(self, fields, rows):
        fp = io.BytesIO()
        workbook = xlsxwriter.Workbook(fp, {'in_memory': True})
        worksheet = workbook.add_worksheet('Sheet 1')

        header_bold_style = workbook.add_format({'text_wrap': True, 'bold': True})
        base_style = workbook.add_format({'text_wrap': True})

        # Write headers
        for i, fieldname in enumerate(fields):
            worksheet.write(0, i, fieldname.get('header_name', ''), header_bold_style)

        # Write rows
        for row_index, row in enumerate(rows):
            for cell_index, cell_value in enumerate(row):
                if isinstance(cell_value, dict):
                    cell_data = cell_value.get('data', '')
                    worksheet.write(row_index + 1, cell_index, cell_data, base_style)

        workbook.close()
        fp.seek(0)
        return base64.b64encode(fp.getvalue()).decode('utf-8')

    @http.route('/web/export/excel_export', type='json', auth="user", methods=['POST'])
    def index(self, **kw):
        # Extract and parse the data from the request

        data = kw
        if isinstance(data, str):
            data = json.loads(data)

        headers = data.get('headers', [])
        rows = data.get('rows', [])

        # Generate the Excel file
        file_content = self.from_data(headers, rows)
        # Return the base64-encoded file content for download
        return {
            'file_content': file_content,
            'file_name': f"{data.get('model', 'export')}.xlsx",
            'file_type': 'application/vnd.ms-excel',
        }
