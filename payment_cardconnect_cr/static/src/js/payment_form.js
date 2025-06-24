odoo.define('payment_cardconnect_cr.payment_form', require => {
    'use strict';

    const core = require('web.core');
    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');
    const _t = core._t;

    const cardConnectMixin = {
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Simulate a feedback from a payment provider and redirect the customer to the status page.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} code - The code of the selected payment option's provider
         * @param {number} paymentOptionId - The id of the selected payment option
         * @param {object} processingValues - The processing values of the transaction
         * @return {Promise}
         */
        _processDirectPayment: function (code, paymentOptionId, processingValues) {
            if (code !== 'cardconnect') {
                return this._super(...arguments);
            }
            const cc_number = document.getElementById('cc_number').value;
            const cc_brand = document.getElementById('cc_brand').value;
            const cc_holder_name = document.getElementById('cc_holder_name').value;
            const cc_expiry = document.getElementById('cc_expiry').value;
            const cc_cvc = document.getElementById('cc_cvc').value;

            if (!cc_number || cc_brand || cc_holder_name || cc_expiry || cc_cvc) {
                if (!cc_number) {
                    $('input#cc_number').addClass('is-invalid o_has_error');
                    $('input#cc_number').removeClass('o_has_success is-valid');
                }
                if (!cc_brand) {
                    $('input#cc_brand').addClass('is-invalid o_has_error');
                    $('input#cc_brand').removeClass('o_has_success is-valid');
                }
                if (!cc_holder_name) {
                    $('input#cc_holder_name').addClass('is-invalid o_has_error');
                    $('input#cc_holder_name').removeClass('o_has_success is-valid');
                }
                if (!cc_expiry) {
                    $('input#cc_expiry').addClass('is-invalid o_has_error');
                    $('input#cc_expiry').removeClass('o_has_success is-valid');
                }
                if (!cc_cvc) {
                    $('input#cc_cvc').addClass('is-invalid o_has_error');
                    $('input#cc_cvc').removeClass('o_has_success is-valid');
                }
            }

            if (cc_number && cc_brand && cc_holder_name && cc_expiry && cc_cvc) {
                return this._rpc({
                    route: '/payment/cardconnect/s2s/create_json_3ds',
                    params: {
                        'reference': processingValues.reference,
                        'acquirer_id': paymentOptionId,
                        'partner_id': processingValues.partner_id,
                        'cc_number': cc_number,
                        'cc_brand': cc_brand,
                        'cc_holder_name': cc_holder_name,
                        'cc_expiry': cc_expiry,
                        'cc_cvc': cc_cvc
                    },
                }).then(paymentResponse => {
                    if (paymentResponse && paymentResponse.error) {
                        this._displayError(
                            _t("Server Error"),
                            _t("We are not able to process your payment."),
                            paymentResponse.error
                        );
                    } else { // The payment reached a final state, redirect to the status page
                        window.location = '/payment/status';
                    }
                }).guardedCatch((error) => {
                    error.event.preventDefault();
                    this._displayError(
                        _t("Server Error"),
                        _t("We are not able to process your payment."),
                        error.message.data.message
                    );
                });
            }
            else {
                return this._displayError(
                    _t("Server Error"),
                    _t("Please Check card details"),
                );
            }
        },

        /**
         * Prepare the inline form of Test for direct payment.
        *
        * @override method from payment.payment_form_mixin
        * @private
        * @param {string} provider - The provider of the selected payment option's acquirer
        * @param {integer} paymentOptionId - The id of the selected payment option
         * @param {string} flow - The online payment flow of the selected payment option
         * @return {Promise}
         */
        _prepareInlineForm: function (provider, paymentOptionId, flow) {
            if (provider !== 'cardconnect') {
                return this._super(...arguments);
            } else if (flow === 'token') {
                return Promise.resolve();
            }
            this._setPaymentFlow('direct');
            return Promise.resolve()
        },
    };

    checkoutForm.include(cardConnectMixin);
    manageForm.include(cardConnectMixin);
});
