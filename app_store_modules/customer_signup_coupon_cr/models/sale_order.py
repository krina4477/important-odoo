from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _apply_program_reward(self, reward, coupon, **kwargs):
        current_email = (self.partner_id.email or "").strip().lower()
        coupon_email = (coupon.partner_id.email or "").strip().lower()

        if coupon_email and current_email != coupon_email:
            return {'error': _('This coupon code is not valid for your account.')}

        return super()._apply_program_reward(
            reward=reward,
            coupon=coupon,
            **kwargs,
        )