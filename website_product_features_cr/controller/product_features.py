from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class ProductFeatureController(http.Controller):

    @http.route('/get_variant_features', type='json', auth='public')
    def get_variant_features(self, product_id=None, **kwargs):
        Product = request.env['product.product'].sudo()
        result = []
        product = Product.browse(int(product_id))
        template = product.product_tmpl_id
        all_feature_lines = template.feature_line_ids

        for line in all_feature_lines:
            if line.product_id and line.product_id.id == product.id:
                result.append({
                    'feature_name': line.feature_id.name,
                    'feature_values': ', '.join(line.feature_value_id.mapped('name')),
                    'product_id': product.id,
                })
            elif not line.product_id:
                result.append({
                    'feature_name': line.feature_id.name,
                    'feature_values': ', '.join(line.feature_value_id.mapped('name')),
                    'product_id': None,
                })

        return {
            'product_id': product.id,
            'features': result,
        }
