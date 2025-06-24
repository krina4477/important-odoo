# -*- encoding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from datetime import date
from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class pharmacyProduct(models.Model):
    _inherit = 'product.product'

    is_medicine = fields.Boolean(string="Is Medicine")
    stock_move_lines = fields.One2many('stock.move.line', 'product_id', string='Stock Move Lines')

    # Define a computed field to check if any variant has not been sold in the last 6 months
    not_sold_in_last_six_months = fields.Boolean(
        string="Not Sold in Last 6 Months",
        compute="_compute_not_sold_in_last_six_months",
        store=True
    )

    @api.depends('stock_move_lines')
    def _compute_not_sold_in_last_six_months(self):
        for product in self:
            if product.is_medicine:
                # Get the date 6 months ago from today
                six_months_ago = datetime.now() - relativedelta(months=6)

                # Check if any stock move line for the product or its variants was created after the six-month mark
                product.not_sold_in_last_six_months = not any(
                    move_line.date >= six_months_ago
                    for move_line in product.stock_move_lines
                )
            else:
                # For non-medicines, explicitly set not_sold_in_last_six_months to False
                product.not_sold_in_last_six_months = False

    # @api.constrains('manufacturing_date')
    # def _valid_mfd_date(self):
    #     today = date.today()
    #     if self.manufacturing_date < today:
    #         raise ValidationError('Manufacturing Must Be Grater Then CurrentDate')
    #
    # @api.constrains('expiry_date')
    # def _valid_exd_date(self):
    #     today = date.today()
    #     if self.expiry_date < today:
    #         raise ValidationError('ExpiryDate is Grater Then the Current date')

    manufacturing_date = fields.Date("Manufacturing Date")
    expiry_date = fields.Date("Expiry Date")

    expiry_note = fields.Char("Expiry Note")
    product_ref_id = fields.Many2one('product.category', string="ref", compute="_compute_decoration")

    def _compute_decoration(self):
        for record in self:
            self_id = self.env.ref("pharmacy.product_category_7")
            if record.categ_id.id == self_id.id:
                record.product_ref_id = self_id.id
            else:
                record.product_ref_id = False

    @api.model
    def cron_expiry_note(self):
        today = fields.Date.today()
        three_months_later = today + timedelta(days=90)
        products_to_update = self.search([('expiry_date', '<=', three_months_later)])

        expiring_soon_category = self.env.ref('pharmacy.product_category_6')

        # Fetch admin's partner information
        admin_user = self.env.ref('base.user_admin')
        admin_partner = admin_user.partner_id

        for product in products_to_update:
            product.categ_id = expiring_soon_category
            product.expiry_note = "(expiring soon)"

            # Send an email notification
            # template = self.env.ref('cr_medical_base.mail_template_product_product')
            product_name = product.name  # Replace with the actual field name of the medicine's name
            subject = f"The medicine '{product_name}' is expiring soon (less than 3 months)."
            body = (f"Dear <strong>'{admin_partner.name}' </strong></br>"
                    f"This is a notification that the medicine <strong>'{product_name}'</strong> is expiring soon (less than 3 months).</br>"
                    f"Please take note of the expiration date: <strong>'{product.expiry_date}'</strong>")

            email_values = {
                'subject': subject,
                'body_html': body,
                'email_from': self.env.user.company_id.email,
                'email_to': admin_partner.email,  # Replace with the appropriate recipient's email
                'model': 'product.product',
                'res_id': product.id,
                # 'template_id': template.id,

            }
            self.env['mail.mail'].create(email_values).send()

        expired_products = self.search([('expiry_date', '<', today)])

        for product in expired_products:
            product.categ_id = self.env.ref('pharmacy.product_category_7')
            product.sale_ok = False
            product.expiry_note = "(expired)"
