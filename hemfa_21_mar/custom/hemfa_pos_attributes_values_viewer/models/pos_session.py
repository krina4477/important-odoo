from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        res = super(PosSession, self)._loader_params_product_product()
        res['search_params']['fields'].append('product_template_attribute_value_ids')
        return res

    def _process_pos_ui_product_product(self, products):
        super(PosSession, self)._process_pos_ui_product_product(products)
        attribute = self.env['product.template.attribute.value']
        for product in products:
            if product['product_template_attribute_value_ids']:
                product['display_name'] = product['display_name']+': '+', '.join(attribute.browse(product['product_template_attribute_value_ids']).mapped('display_name'))
                product['name'] = product['name']+': '+', '.join(attribute.browse(product['product_template_attribute_value_ids']).mapped('display_name'))
            del product['product_template_attribute_value_ids']