# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
from odoo import models, fields, api, _

class WebsiteSeoRedirection(models.Model):
    _name = "website.seo.redirection"
    _rec_name = "destination"
    _order = "destination"
    _description = "SEO controller redirections"
    _sql_constraints = [
        ("origin_unique", "UNIQUE(origin)", "Duplicated original URL"),
        ("origin_destination_distinct",
         "CHECK(origin != destination)",
         "Recursive redirection."),
    ]

    origin = fields.Char(
        string="Original URL",
        index=True,
        help="Path where the original controller was found.",
    )
    destination = fields.Char(
        string="Destination URL",
        required=True,
        index=True,
        help="Path where the controller will be found now.",
    )

    @api.constrains("origin")
    def _check_origin(self):
        self._url_format_check("origin")

    @api.constrains("destination")
    def _check_destination(self):
        self._url_format_check("destination")

    @api.constrains("origin", "destination")
    def _check_not_recursive(self):
        """Avoid infinite loops."""
        for redirection in self:
            origins = {redirection.origin}
            while redirection:
                redirection = self.search([
                    ("origin", "=", redirection.destination),
                ])
                origins.add(redirection.origin)

    def _url_format_check(self, field_name):
        display = self._fields[field_name].string
        for s in self:
            value = s[field_name]
            if not value.startswith("/"):
                raise ValidationError(_("%s must start with `/`") % display)
            for char in "?&=#":
                if char in value:
                    raise ValidationError(
                        _("Invalid character found in %s: `%s`") %
                        (display, char))
            if s.origin == s.destination:
                raise ValidationError(
                    _("You cannot redirect an URL to itself."))

    @api.model
    def create(self, vals):
        result = super(WebsiteSeoRedirection, self).create(vals)
        if vals.get('origin', False) or vals.get('destination', False):
            res = self.env['blog.post'].search([('website_url_latest', '=', result.origin)], limit=1)
            res and res.with_context(update_url=True).write({'destination_url': result.destination})
        return result

    def write(self, vals):
        result = super(WebsiteSeoRedirection, self).write(vals)
        if (vals.get('origin', False)) or vals.get('destination', False):
            res = self.env['blog.post'].search([('website_url_latest','=', self.origin)], limit=1)
            res and res.with_context(update_url=True).write({'destination_url': self.destination})
        return result
