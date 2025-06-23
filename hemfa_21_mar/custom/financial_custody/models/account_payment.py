from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    custody_request_id = fields.Many2one('financial.custody.request', string="Custody Request")

    def action_post(self):
        for payment in self:
            # If the payment is linked to a custody request, check the remaining amounts
            if payment.custody_request_id:
                custody_request = payment.custody_request_id
                remaining_to_pay = round(custody_request.remaining_amount_to_pay, 2)
                remaining_to_receive = round(custody_request.remaining_amount_to_receive, 2)
                payment_amount = round(payment.amount, 2)

                if payment.payment_type == 'outbound' and payment_amount > remaining_to_pay:
                    raise ValidationError(
                        _("The payment amount (%s) exceeds the remaining amount to pay to the employee (%s).") 
                        % (payment_amount, remaining_to_pay)
                    )

                if payment.payment_type == 'inbound' and payment_amount > remaining_to_receive:
                    raise ValidationError(
                        _("The payment amount (%s) exceeds the remaining amount to receive from the employee (%s).") 
                        % (payment_amount, remaining_to_receive)
                    )
                
                # Ensure that the payment journal entry receives the is_cash_request_related flag
                payment.move_id.write({
                    'is_cash_request_related': True,  # Set the flag to true
                })

        # Proceed with the default action_post logic
        return super(AccountPayment, self).action_post()
