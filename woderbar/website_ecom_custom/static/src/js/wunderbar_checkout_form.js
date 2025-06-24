odoo.define('website_ecom_custom.wunderbar_checkout_form', require => {
    'use strict';

    const publicWidget = require('web.public.widget');
    const paymentFormMixin = require('payment.payment_form_mixin');

    publicWidget.registry.WunderbarPaymentCheckoutForm = publicWidget.registry.PaymentCheckoutForm.extend(paymentFormMixin, {

        selector: '#cart_summary_wonderbar',
        events: _.extend({}, publicWidget.Widget.prototype.events, {
            'click div.cart_express_btn': '_onClickPaypal',
        }),

        init: function () {
            this._super(...arguments);
        },

        _onClickPaypal: function (ev) {
            let i = 0
            while (i < $('.o_payment_option_card input').length) {
                if ($('.o_payment_option_card input')[i].dataset.provider == "paypal") {
                    var checkedRadio = $('.o_payment_option_card input')[i]
                }
                i++
            }
            $(checkedRadio).selected(true)
            $('div #payment_method .o_payment_form div button.btn').click()
        },
    });

    return publicWidget.registry.WunderbarPaymentCheckoutForm
});
