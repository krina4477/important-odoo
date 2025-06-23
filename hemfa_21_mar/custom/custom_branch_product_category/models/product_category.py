from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'

    branch_ids = fields.Many2many(
        'res.branch', 
        'product_category_branch_rel', 
        'category_id', 
        'branch_id', 
        string="Branches", 
        help="Branches assigned to this product category. If no branch is selected, it will be available for all branches."
    )
