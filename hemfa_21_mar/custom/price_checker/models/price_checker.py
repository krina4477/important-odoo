from odoo import models, fields, api
from collections import defaultdict


class PriceChecker(models.TransientModel):
    _name = 'price.checker'
    _description = 'Price Checker'
    _rec_name = 'last_scanned_barcode'

    barcode = fields.Char(string="Barcode")
    last_scanned_barcode = fields.Char(string="Last Scanned Barcode", readonly=True)  
    product_template_id = fields.Many2one('product.template', string="Product Template", readonly=True)
    variant_ids = fields.One2many('product.product', string="Product Variants", compute="_compute_variants", readonly=True, store=False)
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist", required=True,
                                   default=lambda self: self.env['product.pricelist'].search([], limit=1))
    selected_warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", ondelete="set null")  
    stock_line_ids = fields.One2many('price.checker.stock.line', 'price_checker_id', string="Stock Information")

    # @api.depends('barcode')
    # def _compute_variants(self):
    #     """ Fetch product variants and recalculate prices when barcode is scanned """
    #     for record in self:
    #         record.variant_ids = False
    #         product = False
    #         if record.barcode:
    #             product_data = self.env['product.product'].read_group([('barcode', '=', record.barcode)], ['id'], [])
    #             product = self.env['product.product'].browse(product_data[0]['id']) if product_data else False
    #
    #         if product:
    #             record.last_scanned_barcode = record.barcode
    #             record.product_template_id = product.product_tmpl_id.id
    #             record.variant_ids = product.product_tmpl_id.product_variant_ids.filtered(lambda v: v.active) or []
    #
    #             # ✅ Ensure all variants have their price computed
    #             for variant in record.variant_ids:
    #                 variant.compute_pricelist_price(record.pricelist_id)
    #
    #             record._compute_stock_lines()
    #         else:
    #             # ❌ Ensure all fields are cleared if barcode is not found
    #             record.last_scanned_barcode = False
    #             record.product_template_id = False
    #             record.variant_ids = []  # ✅ Fix CacheMiss issue
    #             record.stock_line_ids = [(5, 0, 0)]  # Clear stock
    #
    #         record.barcode = ""  # ✅ Reset barcode field after scanning

    @api.depends('barcode')
    def _compute_variants(self):
        """ Fetch product variants and recalculate prices when barcode is scanned """
        for record in self:
            record.variant_ids = [(5, 0, 0)]
            record.last_scanned_barcode = False
            record.product_template_id = False
            record.stock_line_ids = [(5, 0, 0)]  # Clear stock

            if record.barcode:
                product = self.env['product.product'].search(
                    [('barcode', '=', record.barcode)], limit=1
                )

                if product:
                    record.last_scanned_barcode = record.barcode
                    record.product_template_id = product.product_tmpl_id.id

                    # ✅ Corrected variant assignment
                    variant_ids = product.product_tmpl_id.with_context(active_test=True).product_variant_ids.ids
                    record.variant_ids = [(6, 0, variant_ids)]

                    record._compute_stock_lines()

            record.barcode = ""  # ✅ Reset barcode field after scanning

    def _compute_stock_lines(self):
        for record in self:
            record.stock_line_ids = [(5, 0, 0)]
            stock_dict = {}

            for variant in record.variant_ids:
                domain = [('product_id', '=', variant.id)]

                # ✅ If a specific warehouse is selected, filter the stock records
                if record.selected_warehouse_id:
                    domain.append(('location_id.warehouse_id', '=', record.selected_warehouse_id.id))

                stock_quants = self.env['stock.quant'].search(domain)

                for quant in stock_quants:
                    warehouse = quant.location_id.warehouse_id
                    if warehouse:
                        key = (variant.id, warehouse.id)

                        # ✅ If the key already exists, sum the quantity
                        if key in stock_dict:
                            stock_dict[key]['quantity'] += quant.quantity
                        else:
                            stock_dict[key] = {
                                'product_variant_id': variant.id,
                                'warehouse_id': warehouse.id,
                                'quantity': quant.quantity,
                                'product_template_attribute_value_ids': [
                                    (6, 0, variant.product_template_attribute_value_ids.ids)
                                ],
                            }

            record.stock_line_ids = [(0, 0, values) for values in stock_dict.values()]


class PriceCheckerStockLine(models.TransientModel):
    _name = 'price.checker.stock.line'
    _description = 'Stock Line for Price Checker'
    _rec_name = 'product_variant_id'

    price_checker_id = fields.Many2one('price.checker', string="Price Checker", ondelete="cascade")
    product_variant_id = fields.Many2one('product.product', string="Variant", readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", readonly=True)
    quantity = fields.Float(string="Quantity", readonly=True)
    product_template_attribute_value_ids = fields.Many2many('product.template.attribute.value', string="Attributes")  # ✅ Added Many2many Field



class ProductProduct(models.Model):
    _inherit = "product.product"

    pricelist_price = fields.Float(string="Pricelist Price", compute="_compute_variant_prices", store=False)
    barcode = fields.Char(index=True, string="Barcode")  # ✅ Add index on product.product

    @api.depends('product_tmpl_id')
    def _compute_variant_prices(self):
        """ Compute pricelist prices dynamically for each variant """
        for variant in self:
            pricelist = self.env['product.pricelist'].search([], limit=1)
            if pricelist:
                variant.pricelist_price = pricelist._get_product_price(
                    product=variant,
                    quantity=1.0,
                    partner=False,
                    uom_id=variant.uom_id.id
                )

    def compute_pricelist_price(self, pricelist):
        """ Compute the pricelist price dynamically when pricelist changes """
        for variant in self:
            variant.pricelist_price = pricelist._get_product_price(
                product=variant,
                quantity=1.0,
                partner=False,
                uom_id=variant.uom_id.id
            )
