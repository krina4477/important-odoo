from odoo import api, fields, models

class SaleOrderline(models.Model):
    _inherit = 'sale.order.line'

    product_barcode = fields.Char(string='Barcode')
    price_unit = fields.Float(
        string="Unit Price",
        compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=False, required=True,precompute= True
    )

    #=== ACTION METHODS ===#

    def action_add_from_catalog(self):
        order = self.env['sale.order'].browse(self.env.context.get('order_id'))
        return order.action_add_from_catalog()
        

    def _get_product_catalog_lines_data(self, **kwargs):
        """ Override of `sale` to add the delivered quantity.

        :rtype: dict
        :return: A dict with the following structure:
            {
                'deliveredQty': float,
                'quantity': float,
                'price': float,
                'readOnly': bool,
            }
        """
        res = super()._get_product_catalog_lines_data(**kwargs)
        res['deliveredQty'] = 0
        return res

    @api.depends('product_id')
    def _compute_price_unit(self):
        for line in self:
            if line.qty_invoiced > 0:
                continue
            if not line.product_uom or not line.product_id or not line.order_id.pricelist_id:
                line.price_unit = 0.0
            else:
                if not line.price_unit:
                    if line.product_barcode:
                        pricelist_id = line.order_id.pricelist_id if line.order_id else False
                        PricelistObj = self.env['product.pricelist.item'].sudo()
                        price = line.with_company(line.company_id)._get_display_price()
                        domain = [
                            ('product_id', '=', line.product_id.id),
                            ('uom_id', '=', line.product_uom.id),
                            ('pricelist_id', '=', pricelist_id.id)
                        ]
                        if line.product_barcode:
                            domain += [('multi_barcode', '=', line.product_barcode)]
                        obj_price_stand = PricelistObj.search(domain, limit=1)
                        if obj_price_stand:
                            line.price_unit = obj_price_stand.fixed_price
                        else:
                            line.price_unit = 0.0
                    else:
                        price = line.with_company(line.company_id)._get_display_price()
                        line.price_unit = line.product_id._get_tax_included_unit_price(
                            line.company_id,
                            line.order_id.currency_id,
                            line.order_id.date_order,
                            'sale',
                            fiscal_position=line.order_id.fiscal_position_id,
                            product_price_unit=price,
                            product_currency=line.currency_id
                        )
