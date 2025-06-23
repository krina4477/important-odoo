# -*- coding: utf-8 -*-

import logging
from xlrd import open_workbook
import xlrd, datetime
_logger = logging.getLogger(__name__)
from odoo import models, fields


class PriceList(models.Model):
    _inherit = 'product.pricelist'

    def migration_product_price_list(self):
        import os
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'products.xlsx')
        wb = open_workbook(
            filename)

        product_tmpl_object = self.env['product.template']
        sabic_price_list_id = self.env.ref(
            'material_purchase_requisitions.product_price_list_sabic_restoration_project')
        price_list_products = sabic_price_list_id.item_ids.mapped('product_tmpl_id').ids
        for s in wb.sheets():
            for row in range(3, s.nrows):
                price = s.cell(row, 2).value
                product_name = s.cell(row, 1).value

                product_id = product_tmpl_object.sudo().search([('name', '=', product_name)])
                if len(product_id) > 1:
                    print("___________ product exist more then one _____________", len(product_id), product_id)
                elif len(product_id) == 1:
                    if product_id.id not in price_list_products:
                        print("_________ product name __________", product_name, "_________ price __________")
                        self.env['product.pricelist.item'].create({
                            'product_tmpl_id': product_id.id,
                            'fixed_price': price,
                            'pricelist_id': sabic_price_list_id.id,

                        })

    def delete_repeated_product(self):
        sabic_price_list_id = self.env.ref(
            'material_purchase_requisitions.product_price_list_sabic_restoration_project')
        item_to_delete = []
        product_of_item_to__delete = []
        for item in sabic_price_list_id.item_ids:
            length_item = len(sabic_price_list_id.item_ids.filtered(lambda line: line.product_tmpl_id.id == item.product_tmpl_id.id))
            if length_item > 1:
                if item.product_tmpl_id.id not in product_of_item_to__delete:
                    product_of_item_to__delete.append(item.product_tmpl_id.id)
                    item_to_delete.append(item.id)
                    print("_____________ length ________",
                          length_item,
                          "________ product name ______",
                          item.product_tmpl_id.name
                          )
        self.env['product.pricelist.item'].search([('id', 'in', item_to_delete)]).unlink()

    def adding_income_account(self):
        product_ids = self.env['product.template'].search([])
        for product in product_ids:
            product.invoice_policy = 'order'
            print('done')
