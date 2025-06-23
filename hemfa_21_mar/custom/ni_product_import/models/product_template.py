# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"


class ProductTemp(models.Model):
    _inherit = 'product.template'

    # is_gen_variant = fields.Boolean(string='generate variant', default=True)
    description = fields.Char('Description')
    product_group = fields.Char('Product Group')
    product_type = fields.Char('Product Type')
    model_name = fields.Char('Model Name')
    extra_field = fields.Char('Extra Field')

    def _create_variant_ids(self):
        auto_gen_variant = self.env['ir.config_parameter'].sudo().get_param(
            'ni_prod_import.auto_gen_variant'
        )
        if auto_gen_variant:
            return super(ProductTemp, self)._create_variant_ids()
        return True
