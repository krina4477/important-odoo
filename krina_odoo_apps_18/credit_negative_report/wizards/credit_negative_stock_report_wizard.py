from odoo import models, fields, api
import io
import xlsxwriter
import base64
import logging
import re

_logger = logging.getLogger(__name__)


class CreditNegativeReport(models.AbstractModel):
    _name = 'report.credit_negative_report.credit_negative_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['credit.negative.stock.wizard'].browse(docids)

        # Fetch all unordered products, grouped by company
        company_product_data = docs._get_negative_products()
        grouped_data_by_company = docs._group_products(company_product_data)

        return {
            'docs': docs,
            'company_grouped': grouped_data_by_company,
        }


class CreditNegativeReportWizard(models.TransientModel):
    _name = 'credit.negative.stock.wizard'
    _description = 'Wizard for Never Sold Report'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    active_company_ids = fields.Many2many('res.company',
                                          'value_company_rel', 'values_id', 'company_id', string="Company",
                                          default=lambda
                                              self: self.env.companies.ids)
    supplier_type = fields.Selection([
        ('all', 'All'),
        ('credit', 'Credit'),
        ('consignment', 'Consignment')
    ], string="Supplier Type", required=True)
    # store_codes = fields.Char(string='Store Codes', compute='_compute_store_codes')
    company_ids = fields.Many2many('res.company', string='Company')
    export_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
    ], string="Print Out", required=True)
    has_child = fields.Boolean(compute="_compute_has_child_companies",
                                         store=True)

    @api.depends('company_ids')
    def _compute_has_child_companies(self):
        for record in self:
            record.has_child = any(company.child_ids for company in record.company_ids)

    def action_download_report(self):
        company_product_data = self._get_negative_products()
        grouped_products = self._group_products(company_product_data)
        if self.export_format == 'pdf':
            return self.env.ref('credit_negative_report.action_credit_negative_report').report_action(self)
        elif self.export_format == 'xlsx':
            return self._export_xlsx(grouped_products)

    def _get_negative_products(self):
        StockQuant = self.env['stock.quant']
        ValuationLayer = self.env['stock.valuation.layer']
        company_product_data = {}
        processed = set()

        for main_company in self.company_ids:
            # Include the main company and all its child companies
            all_companies = main_company | main_company.child_ids

            for company in all_companies:
                domain = [
                    ('quantity', '<', 0),
                    ('company_id', '=', company.id)
                ]
                negative_quants = StockQuant.search(domain)
                company_product_data[company] = []

                for quant in negative_quants:
                    product = quant.product_id
                    if not product:
                        continue

                    key = (company.id, product.id)
                    if key in processed:
                        continue

                    # Look into valuation layers within the date range
                    val_layer_domain = [
                        ('product_id', '=', product.id),
                        ('company_id', '=', company.id),
                        ('create_date', '>=', self.start_date),
                        ('create_date', '<=', self.end_date),
                    ]
                    recent_layers = ValuationLayer.search(val_layer_domain, limit=1)

                    if not recent_layers:
                        continue  # Skip if no valuation activity during the period

                    processed.add(key)

                    supplier_names = product.seller_ids.mapped('partner_id')
                    if self.supplier_type == 'credit':
                        if not any(getattr(s, 'trade_term', '') == 'credit' for s in supplier_names):
                            continue
                    elif self.supplier_type == 'consignment':
                        if not any(s.trade_term == 'consignment' for s in supplier_names):
                            continue

                    category = product.categ_id

                    company_product_data[company].append({
                        'div_name': category.name or '',
                        'dept_name': category.department_name or '',
                        'sub_dept_name': category.sub_department_name or '',
                        'store_code': company.pc_code or '',
                        'product_name': product.name or '',
                        'product_id': product.id or '',
                        'barcode': product.barcode or '',
                        'cogs': product.standard_price,
                        'stock_qty': quant.quantity,
                        'stock_amount': product.standard_price * quant.quantity,
                    })

        return company_product_data

    def _group_products(self, company_product_data):
        grouped = {}
        for company, products in company_product_data.items():
            grouped[company] = {}
            for product in products:
                div = product.get('div_name', 'No Division')
                if div not in grouped[company]:
                    grouped[company][div] = []
                grouped[company][div].append(product)
        return grouped

    def _export_xlsx(self, grouped_products):
        if not any(grouped_products.values()):
            pass
            # raise UserError("No negative stock data found for the selected criteria.")

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        # Define styles
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        text_format = workbook.add_format({
            'border': 1,
            'valign': 'vcenter',
            'text_wrap': True
        })
        currency_format = workbook.add_format({
            'border': 1,
            'valign': 'vcenter',
            'num_format': '#,##0.00'
        })
        number_format = workbook.add_format({
            'border': 1,
            'valign': 'vcenter',
            'num_format': '#,##0'
        })

        for company in grouped_products.keys():
            all_companies = [company] + list(company.child_ids)

            for comp in all_companies:
                comp_divisions = grouped_products.get(comp)
                if not comp_divisions:
                    continue  # Skip if no data for this company

                comp_name = comp.name or "NA"
                pc_code = comp.pc_code or "NA"
                sheet_name_raw = f"{comp_name}-{pc_code}"
                sheet_name = re.sub(r'[\\/*?:[\]]', '_', sheet_name_raw)[:31]
                sheet = workbook.add_worksheet(name=sheet_name)

                # Freeze header
                sheet.freeze_panes(2, 0)

                # Write top header
                sheet.merge_range('A1:J1', f"Company: {comp_name} (Code: {pc_code})", header_format)

                # Table headers
                headers = [
                    'No', 'Div Name', 'Dept Name', 'Sub-dept Name',
                    'Product ID', 'Barcode', 'Product Name',
                    'COGS', 'Stock Qty', 'Stock Amount'
                ]
                column_widths = [10, 20, 20, 25, 15, 15, 30, 12, 12, 15]
                for col, (header, width) in enumerate(zip(headers, column_widths)):
                    sheet.write(1, col, header, header_format)
                    sheet.set_column(col, col, width)

                # Adjust width based on content length
                sub_dept_lengths = [
                    len(product['sub_dept_name'])
                    for division_products in comp_divisions.values()
                    for product in division_products
                ]
                max_sub_dept_name_length = max(sub_dept_lengths) + 5 if sub_dept_lengths else 30
                sheet.set_column(3, 3, max(25, max_sub_dept_name_length))

                product_name_lengths = [
                    len(product['product_name'])
                    for division_products in comp_divisions.values()
                    for product in division_products
                ]
                max_product_name_length = max(product_name_lengths) + 5 if product_name_lengths else 30
                sheet.set_column(6, 6, max(30, max_product_name_length))

                # Write data
                row = 2
                product_index = 1
                for division_products in comp_divisions.values():
                    for product in division_products:
                        sheet.write(row, 0, product_index, number_format)
                        sheet.write(row, 1, product['div_name'], text_format)
                        sheet.write(row, 2, product['dept_name'], text_format)
                        sheet.write(row, 3, product['sub_dept_name'], text_format)
                        sheet.write(row, 4, product['product_id'], number_format)
                        sheet.write(row, 5, product['barcode'], text_format)
                        sheet.write(row, 6, product['product_name'], text_format)
                        sheet.write(row, 7, product['cogs'], currency_format)
                        sheet.write(row, 8, product['stock_qty'], number_format)
                        sheet.write(row, 9, product['stock_amount'], currency_format)
                        row += 1
                        product_index += 1

        workbook.close()
        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': 'credit_negative_stock_report.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }








