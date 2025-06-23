/** @odoo-module */
/* global Stripe */

import { _t } from '@web/core/l10n/translation';
import paymentForm from '@payment/js/payment_form';
//import { jsonrpc } from "@web/core/network/rpc_service";
import { rpc } from "@web/core/network/rpc";

paymentForm.include({
    display_securionpay_form: function(provider_form) {
    var provider_form = provider_form.redirect_form_html
            SecurionpayCheckout.success = function(result) {
                $('.securionpay_loading').show();
                result['reference'] = $(provider_form).find('input[name="reference"]').val();
                result['amount'] = $(provider_form).find('input[name="amount"]').val();

                rpc('/securianpay/validate', result).then(function(data) {
                    if (data.status) {
                        $('.securionpay_loading').hide();
                        window.location.href = '/shop/payment/validate'
                    }
                });
            };
            SecurionpayCheckout.error = function(errorMessage) {
                window.location.pathname = '/shop'
            };
            SecurionpayCheckout.key = $(provider_form).find('input[name="key"]').val()
            var payment_form = $('.o_payment_form');
            var provider_id = $(provider_form).find('input[name="provider_id"]').val();
            if (!provider_id) {
                return false;
            }

            var access_token = $(provider_form).find('input[name="csrf_token"]').val() || '';
            var so_id = $(provider_form).find('input[name="so_id"]').val() || undefined;

            $('.securionpay_loading').show();

            var amount = $(provider_form).find('input[name="amount"]').val();
            var partner_id = $(provider_form).find('input[name="partner_id"]').val();
            var currency_id = $(provider_form).find('input[name="currency_id"]').val();
            var landing_route = $(provider_form).find('input[name="landing_route"]').val();
            var $pay_securionpay = $('#pay_securionpay').detach();
            // Restore 'Pay Now' button HTML since data might have changed it.
            $(provider_form).find('#pay_securionpay').replaceWith($pay_securionpay);
            var checkout_request = $(provider_form).find('input[name="checkout_request"]').val()
            $('.securionpay_loading').hide();
            SecurionpayCheckout.open({
                checkoutRequest: checkout_request.toString(),
                name: $(provider_form).find('input[name="company"]').val(),
                description: $(provider_form).find('input[name="description"]').val(),
                image: $(provider_form).find('input[name="image"]').val(),
                email: $(provider_form).find('input[name="email"]').val(),
            });
        },

    _processRedirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode != "securionpay") {
            return this._super(...arguments);
        }
        this.display_securionpay_form(processingValues);
    },

});
