from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import io
from datetime import datetime
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_diff = fields.Float(
        string='Difference',
        compute='_compute_qty_diff',
        store=True,  # This is required for sorting
        help="Difference between Done and Demand"
    )

    @api.depends('quantity_done', 'product_uom_qty')
    def _compute_qty_diff(self):
        for record in self:
            record.qty_diff = record.quantity_done - record.product_uom_qty


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_export_qty_diff(self):
        # Check if xlsxwriter is installed
        if not xlsxwriter:
            raise UserError("xlsxwriter is not installed. Install it using: pip install XlsxWriter")

        # Filter lines with qty_diff != 0
        move_lines = self.move_ids_without_package.filtered(lambda line: line.qty_diff != 0)
        if not move_lines:
            raise UserError("No lines with differences found.")

        # Create an in-memory Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet('Qty Differences')

        # Define formats
        bold = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})  # Grey background for headers
        red = workbook.add_format({'font_color': 'red'})
        green = workbook.add_format({'font_color': 'green'})

        # Write headers
        headers = ['Product', 'Internal Reference', 'Barcode', 'Demand Quantity', 'Done Quantity', 'Difference']
        for col_num, header in enumerate(headers):
            sheet.write(0, col_num, header, bold)

        # Write data rows
        row = 1
        for line in move_lines:
            product = line.product_id
            # Fetch barcode and internal reference for the product or variant
            barcode = product.barcode or ''  # Get the barcode or leave blank if not available
            internal_ref = product.default_code or ''  # Get internal reference or leave blank if not available
            sheet.write(row, 0, product.name)
            sheet.write(row, 1, internal_ref)
            sheet.write(row, 2, barcode)
            sheet.write(row, 3, line.product_uom_qty)
            sheet.write(row, 4, line.quantity_done)
            # Apply conditional coloring for Difference
            if line.qty_diff > 0:
                sheet.write(row, 5, line.qty_diff, green)
            else:
                sheet.write(row, 5, line.qty_diff, red)
            row += 1

        workbook.close()
        output.seek(0)

        # Prepare file for download
        export_file_name = f"qty_difference_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': export_file_name,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': 'stock.picking',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        output.close()

        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }
