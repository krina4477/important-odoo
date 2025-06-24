from odoo import fields, models


class x_radio(models.Model):
    _name = "x_radio"
    _inherit = ["x_radio", "website_seo_url"]

    seo_url = fields.Char("SEO URL", translate=True, index=True)
