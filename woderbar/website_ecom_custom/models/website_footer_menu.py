from odoo import fields, models


class WebsiteFooterMenu(models.Model):

    _name = 'website.footer.menu'
    _description = 'Website Footer Menu'

    name = fields.Char('Menu', required=True, translate=True)
    url = fields.Char('Url', required=True)
    website_id = fields.Many2one('website', 'Website', ondelete='cascade')


class Website(models.Model):

    _inherit = "website"

    def _compute_footer_menu(self):
        for website in self:
            website.footer_menu_ids = self.env['website.footer.menu'].search([('website_id', '=', self.id)]).ids

    footer_menu_ids = fields.Many2many('website.footer.menu', compute='_compute_footer_menu', string='Footer Menu')

    def product_info_sale_get_order(self, prod_qty,product_id):
        self.ensure_one()
        partner = self.env.user.partner_id
        sale_order_rec = self.env['sale.order'].search([('product_shop','=',True),('partner_id', '=', partner.id),('state', '=', 'draft')],limit=1)
        
        if sale_order_rec:
            vals = {
                'order_line' : [(5,0,0),(0,0,{
                                    'product_id': int(product_id),
                                    'product_uom_qty': int(prod_qty)})]}
            sale_order = sale_order_rec.write(vals)
            return sale_order_rec
            
        else:
            vals = {
                'partner_id' : partner.id,
                'order_line' : [(0,0,{'product_id': int(product_id),
                                    'product_uom_qty': int(prod_qty)})],
                'product_shop' : True
                }
            sale_order = self.env['sale.order'].create(vals)
            return sale_order
