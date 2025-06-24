# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class Product(models.Model):
    _inherit = 'product.template'

    manufacture_year_id = fields.Many2many('x_fahrzeug_baujahr')
    feature_id = fields.Many2one("product.feature")
    vehicle_model_id = fields.Many2many('x_fahrzeug_modell')
    technical_specification = fields.Html(translate=True)
    manufacture_name = fields.Selection([
        ('ACADIAN', 'ACADIAN'),
        ('BEAUMONT', 'BEAUMONT'),
        ('BUICK', 'BUICK'),
        ('CADILLAC', 'CADILLAC'),
        ('CHEVROLET', 'CHEVROLET'),
        ('CHRYSLER', 'CHRYSLER'),
        ('GENERAL MOTORS', 'GENERAL MOTORS'),
        ('GM', 'GM'),
        ('GMC', 'GMC'),
        ('GMC', 'GMC'),
        ('LINCOLN', 'LINCOLN'),
        ('OLDSMOBILE', 'OLDSMOBILE'),
        ('PONTIAC', 'PONTIAC'),
        ('STUDEBAKER', 'STUDEBAKER'),
        ('ALFA ROMEO', 'ALFA ROMEO'),
        ('BENTLEY', 'BENTLEY'),
        ('AMC', 'AMC'),
        ('DE LOREAN', 'DE LOREAN'),
        ('BMW', 'BMW'),
        ('DODGE', 'DODGE'),
        ('LOTUS', 'LOTUS'),
        ('OPEL', 'OPEL'),
        ('TRIUMPH', 'TRIUMPH'),
        ('VOLKSWAGEN', 'VOLKSWAGEN'),
        ('VOLVO', 'VOLVO'),
        ('FORD', 'FORD'),
        ('MERCEDES - BENZ', 'MERCEDES - BENZ'),
        ('AUTO UNION', 'AUTO UNION'),
        ], 'Manufacturer', default='ACADIAN')

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        combination_info = super(Product, self)._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template,
        )

        if combination_info['product_id']:
            product = self.env['product.product'].sudo().browse(combination_info["product_id"])
            combination_info['description_sale'] = product.description_sale

        return combination_info

class ProductFeature(models.Model):
    _name = "product.feature"
    _description = "Product Feature"

    name = fields.Char()


# class WebsiteMenu(models.Model):
#     _inherit = "website.menu"

    # @api.model
    # def create(self, vals_list):
    #     res = super(WebsiteMenu, self).create(vals_list)
    #     for menu in res:
    #         if not menu.parent_id and menu.website_id:
    #         	menu.parent_id = menu.website_id.menu_id.id
    #     return res
