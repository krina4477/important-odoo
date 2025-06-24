odoo.define('website_ecom_custom.wunderbar_shop_product_checkout_form', require => {
    'use strict';

    const core = require('web.core');
    const _t = core._t;
    const publicWidget = require('web.public.widget');
    const paymentFormMixin = require('payment.payment_form_mixin');

    publicWidget.registry.WunderbarShopProductPaymentCheckoutForm = publicWidget.registry.PaymentCheckoutForm.extend(paymentFormMixin, {

        selector: '.js_main_product',
        events: _.extend({}, publicWidget.Widget.prototype.events, {
            'click #paypal_btn_wrap': '_onClickProductPaypal',
        }),

        init: function () {
            this._super(...arguments);
        },

        _onClickProductPaypal: function (ev) {
            var input_val = $("input[name*='add_qty']").val();
            var product_id = $("input.product_id").val();
            var product_template_id = $("input.product_template_id").val();
            this._rpc({
                route: '/shop/product/paypal_payment',
                params: {
                    'prod_qty': input_val,
                    'product_id': product_id,
                    'product_template_id': product_template_id
                },
            }).then(data => {
                var provider = data.paymentacquirer
                var paymentOptionId = data.paymentOptionId
                var flow = this.txContext.flow
                this._rpc({
                    route: data.transaction_route,
                    params: this._paypalpaymentprepareTransactionRouteParams(provider, paymentOptionId, flow, data),
                }).then(processingValues => {
                    if (flow === 'redirect') {
                        return this._processRedirectPayment(
                            provider, paymentOptionId, processingValues
                        );
                    } else if (flow === 'direct') {
                        return this._processDirectPayment(provider, paymentOptionId, processingValues);
                    } else if (flow === 'token') {
                        return this._processTokenPayment(provider, paymentOptionId, processingValues);
                    }
                }).guardedCatch(error => {
                    error.event.preventDefault();
                    this._displayError(
                        _t("Server Error"),
                        _t("We are not able to process your payment."),
                        error.message.data.message
                    );
                });
            });
        },

        _paypalpaymentprepareTransactionRouteParams: function (provider, paymentOptionId, flow, data) {
            return {
                'payment_option_id': paymentOptionId,
                'amount': data.amount !== undefined
                    ? parseFloat(data.amount) : null,
                'currency_id': data.currencyId
                    ? parseInt(data.currencyId) : null,
                'partner_id': parseInt(data.partner_id),
                'flow': flow,
                'tokenization_requested': false,
                'landing_route': data.landing_route,
                'access_token': data.access_token
                    ? data.access_token : undefined,
                'csrf_token': core.csrf_token,
            };
        },
    });

    return publicWidget.registry.WunderbarShopProductPaymentCheckoutForm
});