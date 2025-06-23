# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo.http import request
from odoo import models, fields

class BlogPost(models.Model):
    _inherit = "blog.post"

    destination_url = fields.Char(string="Destination URL", index=True,
        help="Path where the controller will be found now.",
    )

    website_url_latest = fields.Char('Website URL', compute='_compute_website_url', store=True,
                              help='The full URL to access the document through the website.')

    def _compute_website_url(self):
        super(BlogPost, self)._compute_website_url()
        import pdb
        pdb.set_trace()
        slug = request.env['ir.http']._slug
        for blog_post in self:
            blog_post.website_url_latest = "/blog/%s/%s" % (slug(blog_post.blog_id), slug(blog_post))

    def write(self, vals):
        result = super().write(vals)
        if self.destination_url and vals.get('destination_url',False) and not self.env.context.get('update_url'):
            res = self.env['website.seo.redirection'].search([('origin','=', self.website_url)], limit=1)
            res and res.write({'destination': self.destination_url})
            if not res:
                self.env['website.seo.redirection'].create({'origin': self.website_url,
                                                            'destination': self.destination_url})
        return result

