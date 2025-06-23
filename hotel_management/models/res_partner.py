from odoo import api, fields, models
from slugify import slugify


class ResPartner(models.Model):
    _inherit = "res.partner"

    # slug = fields.Char('Slug', compute='_compute_slug', store=True)

    # @api.depends('name')
    # def _compute_slug(self):
    #     for partner in self:
    #         partner.slug = slugify(partner.name)

    def confirm_booking(self):
        # Call the super method to perform the default behavior of the confirm_order method

        return {
            'name': 'Timesheet',
            'domain': [('customer_id', '=', self.id)],
            'res_model': 'booking.form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
