from odoo import models,fields

class widget(models.Model):
    _inherit = "product.template"
    _description="add widget field in X_website_description"

    x_website_description=fields.Char(string="Website Description",store=True )


    def save(self, resid,table ):
        product_tmpl_id = self.browse([resid])
        product_tmpl_id.write({'x_website_description': table})
        self.env.cr.execute("""UPDATE product_template SET x_website_description = '%s' where id = %s"""%(table, product_tmpl_id.id))
        return True
