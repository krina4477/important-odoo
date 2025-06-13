from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route
from datetime import datetime, timedelta

class WebsiteSaleAddressCustom(WebsiteSale):
	@route(['/shop/address/submit'], type='http', auth="public", website=True, csrf=False)
	def shop_address_submit(
		self, partner_id=None, address_type='billing', use_delivery_as_billing=None, callback=None,
		required_fields=None, **form_data
	):
		# Call the original method to save the address
		response = super().shop_address_submit(
			partner_id=partner_id,
			address_type=address_type,
			use_delivery_as_billing=use_delivery_as_billing,
			callback=callback,
			required_fields=required_fields,
			**form_data
		)

		# Get the POS send mail setting from system parameters and convert to boolean
		is_send_mail = request.env['ir.config_parameter'].sudo().get_param('customer_signup_coupon_cr.is_send_mail')
		is_send_mail = is_send_mail in ['1', 'True', 'true']

		if is_send_mail:
			email = form_data.get('email') or form_data.get('email_from')
			partner = None
			# program = request.env['loyalty.program'].sudo().search([('program_type', '=', 'coupons')], limit=1)
			program = request.env.company.signup_program_id
			if email:
				# Try to find the partner by email
				partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
			if not partner:
				# Try to get partner from session (if available)
				session_partner_id = request.session.get('partner_id')
				if session_partner_id:
					partner = request.env['res.partner'].sudo().browse(session_partner_id)

			if partner and email and program:
				coupon_value = 10
				valid_until = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

				# Create loyalty card/gift card
				loyalty_card = request.env['loyalty.card'].sudo().create({
					'partner_id': partner.id,
					'program_id': program.id if program else False,
					'expiration_date': valid_until,
					'points': 1,
				})
				mail_values = {
					'subject': 'Your Gift Card Coupon Code',
					'body_html': f"""
						<p>Dear {partner.name},</p>
						<p>Thank you for signing in!</p>
						<p>As a token of our appreciation, here is your exclusive gift card coupon:</p>
						<h2 style="color:#1976d2;">{loyalty_card.code}</h2>
						<p>
							<b>Value:</b> {coupon_value}%
							<br><b>Valid Until:</b> {valid_until}
							<br><b>How to use:</b> Enter the code at checkout.
							<br><b>Valid for:</b> One use per customer.
						</p>
						<p>Happy shopping!<br>The {request.env.user.company_id.name} Team</p>
					""",
					'email_to': email,
					'email_from': request.env.user.company_id.email or 'no-reply@example.com',
					'auto_delete': True,
				}
				mail = request.env['mail.mail'].sudo().create(mail_values)
				mail.sudo().send()
		return response