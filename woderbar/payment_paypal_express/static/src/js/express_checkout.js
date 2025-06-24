/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('payment_paypal_express.express_checkout', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var PaymentForm = require('payment.checkout_form');
    var ajax = require('web.ajax');

    var core = require('web.core');
    var _t = core._t;

    function get_payer_data(data_values){
        var payer = {}
        if(!data_values){
            return payer
        }
        if (!data_values.billing_country_code || !data_values.billing_zip_code || !data_values.billing_area2){
            return payer
          }
        if(data_values.billing_first_name || data_values.billing_last_name){
            var name = {}
            if(data_values.billing_first_name){
                name['given_name'] = data_values.billing_first_name
            }
            if(data_values.billing_last_name){
                name['surname'] = data_values.billing_last_name
            }
            payer['name'] = name
        }
        var address = {}
        if(data_values.billing_address_l1){
            address['address_line_1'] = data_values.billing_address_l1
        }
        if(data_values.billing_area2){
            address['admin_area_2'] = data_values.billing_area2
        }
        if(data_values.billing_area1){
            address['admin_area_1'] = data_values.billing_area1
        }
        if(data_values.billing_zip_code){
            address['postal_code'] = data_values.billing_zip_code
        }
        if(data_values.billing_country_code){
            address['country_code'] = data_values.billing_country_code
        }
        payer['address'] = address
        if(data_values.billing_email){
            payer['email_address'] = data_values.billing_email
        }
        if(data_values.billing_phone.match('^[0-9]{1,14}?$')){
            payer['phone'] = {
                phone_type: "MOBILE",
                phone_number: {
                    national_number: data_values.billing_phone,
                }
            }
        }
        return payer
    }
    function get_shipping_data(data_values){
        var shipping = {}
        if(!data_values){
            return shipping
        }
        if (!data_values.shipping_country_code || !data_values.shipping_zip_code || !data_values.shipping_area2){
            return shipping
          }
        if(data_values.shipping_partner_name){
            shipping['name'] = {
                full_name: data_values.shipping_partner_name,
            }
        }
        var shipping_address = {}
        if(data_values.shipping_address_l1){
            shipping_address['address_line_1'] = data_values.shipping_address_l1
        }
        if(data_values.shipping_area2){
            shipping_address['admin_area_2'] = data_values.shipping_area2
        }
        if(data_values.shipping_area1){
            shipping_address['admin_area_1'] = data_values.shipping_area1
        }
        if(data_values.shipping_zip_code){
            shipping_address['postal_code'] = data_values.shipping_zip_code
        }
        if(data_values.shipping_country_code){
            shipping_address['country_code'] = data_values.shipping_country_code
        }
        shipping['address'] = shipping_address
        return shipping
    }

    PaymentForm.include({
      willStart: function(){
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            return self._rpc({
                route: '/paypal/express/checkout/url',
                params: {}
            }).then(function(url){
                if(url){
                    return ajax.loadJS(url).then(function(){
                        if (self.$el.length>0 && $(self.$el[0]).hasClass('o_payment_form')){
                          self.checkout_override();
                        }

                    });
                }
            });
        });
      },

        start: async function () {
            await this._super(...arguments);
            // if ($(this.$el[0]).hasClass('o_payment_form')){
            const $checkedRadios = this.$('input[name="o_payment_radio"]:checked');
             if (this.$el.length>0 && $(this.$el[0]).hasClass('o_payment_form')){
                 $('#paypal-button').hide();
             }
            if ($checkedRadios.length === 1) {
                const checkedRadio = $checkedRadios[0];
                this._displayInlineForm(checkedRadio);
                if($checkedRadios.attr('data-provider') == 'paypal_express'){
                    $("button[name='o_payment_submit_button']").hide();
                    $('#paypal-button').show();
                }else{
                    this._enableButton();
                }
            }
            // }
        },
        get_btn_style: function(){
            return {
                size: 'small',
                // color: 'blue',
                color:   'gold',
                shape: 'pill',
                label:  'pay',
                }
        },
        order_values: async function () {
           var self = this;
           var form = $('form[name="o_payment_checkout"]');
           var checked_radio = form.find('input[type="radio"]:checked');
           if (checked_radio.length !== 1) {
               return;
           }
           checked_radio = checked_radio[0];
           var provider = checked_radio.dataset.provider;
           if(provider === 'paypal_express'){
               var values = self.txContext;
               this.txContext.tokenizationRequested = false;
               this.txContext.is_validation = false;
                   return self._rpc({
                       route:  self.txContext.transactionRoute,
                       params: this._prepareTransactionRouteParams('paypal_express',$(checked_radio).data("payment-option-id"),'redirect'),
                   }).then(function (result) {
                       var newform = document.createElement('div');
                       var $newform = $(newform)
                       $newform.append(result["redirect_form_html"]);
                       return {
                           amount : parseFloat($newform.find('input[name="amount"]').val()).toFixed(2),
                           reference : $newform.find('input[name="invoice_num"]').val(),
                           so_reference : $newform.find('input[name="so_reference"]').val(),
                           currency_code : $newform.find('input[name="currency_code"]').val(),
                           billing_first_name: $newform.find('input[name="billing_first_name"]').val(),
                           billing_last_name: $newform.find('input[name="billing_last_name"]').val(),
                           billing_phone: $newform.find('input[name="billing_phone"]').val(),
                           billing_email: $newform.find('input[name="billing_email"]').val(),
                           billing_address_l1: $newform.find('input[name="billing_address_l1"]').val(),
                           billing_area1: $newform.find('input[name="billing_area1"]').val(),
                           billing_area2: $newform.find('input[name="billing_area2"]').val(),
                           billing_zip_code: $newform.find('input[name="billing_zip_code"]').val(),
                           billing_country_code: $newform.find('input[name="billing_country_code"]').val(),
                           shipping_partner_name: $newform.find('input[name="shipping_partner_name"]').val(),
                           shipping_address_l1: $newform.find('input[name="shipping_address_l1"]').val(),
                           shipping_area1: $newform.find('input[name="shipping_area1"]').val(),
                           shipping_area2: $newform.find('input[name="shipping_area2"]').val(),
                           shipping_zip_code: $newform.find('input[name="shipping_zip_code"]').val(),
                           shipping_country_code: $newform.find('input[name="shipping_country_code"]').val(),
                       };
                   }).catch((err)=>{
                     console.log("Error while creating transaction ---",err)
                   });
               }
           },
       checkout_override: function () {

           var self = this;
           var loader = $('#paypal_express_loader');
           paypal.Buttons({
               style: self.get_btn_style(),
               createOrder: function(data, actions) {
                   loader.show();
                   return self.order_values().then(function (values){
                       loader.hide();
                       return actions.order.create({
                           payer: get_payer_data(values),
                           purchase_units: [{
                               amount: {
                                   value: values.amount,
                                   currency_code: values.currency_code
                               },
                               description: values.so_reference,
                               reference_id: values.reference,
                               shipping: get_shipping_data(values),
                           }],
                       });
                   });
               },
               onApprove: function(data, actions) {
                   loader.show();
                   return actions.order.capture()
                   .then(function (details) {
                       self._rpc({
                           route: '/paypal/express/checkout/state',
                           params: details
                       }).then(function(result){
                           window.location.href = window.location.origin + result
                           loader.hide();
                       });
                   });
               },
               onCancel: function (data, actions) {
                   loader.show();
                   self._rpc({
                       route: '/paypal/express/checkout/cancel',
                       params: data
                   }).then(function(result){
                       window.location.href = window.location.origin + result
                       loader.hide();
                   });
               },
               onError: function (error) {
                   loader.hide();
                   return alert(error);
               }
           }).render('#paypal-button');
       },
        _onClickPaymentOption: function () {
            this._super.apply(this, arguments);
            var checked_radio = this.$('input[type="radio"]:checked');
            if (checked_radio.length !== 1) {
                return;
            }
            checked_radio = checked_radio[0];
            var provider = checked_radio.dataset.provider
            if(provider == 'paypal_express'){
                $("button[name='o_payment_submit_button']").hide();
                $('#paypal-button').show();
            }
            else{
                $('#paypal-button').hide();
                $("button[name='o_payment_submit_button']").show();
            }
        },
    });

    return publicWidget.registry.PaypalCheckoutButton;
});


odoo.define('payment_paypal_express.mobile_express_checkout', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var PaymentForm = require('payment.checkout_form');
    var ajax = require('web.ajax');

    var core = require('web.core');
    var _t = core._t;

    function get_payer_data(data_values){
        var payer = {}
        if(!data_values){
            return payer
        }
        if (!data_values.billing_country_code || !data_values.billing_zip_code || !data_values.billing_area2){
            return payer
          }
        if(data_values.billing_first_name || data_values.billing_last_name){
            var name = {}
            if(data_values.billing_first_name){
                name['given_name'] = data_values.billing_first_name
            }
            if(data_values.billing_last_name){
                name['surname'] = data_values.billing_last_name
            }
            payer['name'] = name
        }
        var address = {}
        if(data_values.billing_address_l1){
            address['address_line_1'] = data_values.billing_address_l1
        }
        if(data_values.billing_area2){
            address['admin_area_2'] = data_values.billing_area2
        }
        if(data_values.billing_area1){
            address['admin_area_1'] = data_values.billing_area1
        }
        if(data_values.billing_zip_code){
            address['postal_code'] = data_values.billing_zip_code
        }
        if(data_values.billing_country_code){
            address['country_code'] = data_values.billing_country_code
        }
        payer['address'] = address
        if(data_values.billing_email){
            payer['email_address'] = data_values.billing_email
        }
        if(data_values.billing_phone.match('^[0-9]{1,14}?$')){
            payer['phone'] = {
                phone_type: "MOBILE",
                phone_number: {
                    national_number: data_values.billing_phone,
                }
            }
        }
        return payer
    }
    function get_shipping_data(data_values){
        var shipping = {}
        if(!data_values){
            return shipping
        }
        if (!data_values.shipping_country_code || !data_values.shipping_zip_code || !data_values.shipping_area2){
            return shipping
          }
        if(data_values.shipping_partner_name){
            shipping['name'] = {
                full_name: data_values.shipping_partner_name,
            }
        }
        var shipping_address = {}
        if(data_values.shipping_address_l1){
            shipping_address['address_line_1'] = data_values.shipping_address_l1
        }
        if(data_values.shipping_area2){
            shipping_address['admin_area_2'] = data_values.shipping_area2
        }
        if(data_values.shipping_area1){
            shipping_address['admin_area_1'] = data_values.shipping_area1
        }
        if(data_values.shipping_zip_code){
            shipping_address['postal_code'] = data_values.shipping_zip_code
        }
        if(data_values.shipping_country_code){
            shipping_address['country_code'] = data_values.shipping_country_code
        }
        shipping['address'] = shipping_address
        return shipping
    }

    // publicWidget.registry.MobilePaypalCheckoutButton = publicWidget.Widget.extend({
    //     selector: '#mobile-paypal-button',
    //     willStart: function () {
    //         var self = this;
    //         return this._super.apply(this, arguments).then(function () {
    //             return self._rpc({
    //                 route: '/paypal/express/checkout/url',
    //                 params: {}
    //             }).then(function(url){
    //                 if(url){
    //                     return ajax.loadJS(url).then(function(){
    //                         self.checkout_override();
    //                     });
    //                 }
    //             });
    //         });
    //     },
    //     get_btn_style: function(){
    //         return {
    //             size: 'small',
    //             color: 'blue',
    //             shape: 'pill',
    //             label:  'pay',
    //             }
    //     },
    //     order_values: function () {
    //         var self = this;
    //         var form = $('form[name="o_payment_checkout"]');
    //         var checked_radio = form.find('input[type="radio"]:checked');
    //         if (checked_radio.length !== 1) {
    //             return;
    //         }
    //         checked_radio = checked_radio[0];
    //         var provider = checked_radio.dataset.provider;
    //         if(provider === 'paypal_express'){
    //             var $tx_url = form.data("transaction-route");
    //             if ($tx_url.length > 1) {
    //                 var txContext = {
    //                     'referencePrefix': form.data("reference-prefix"),
    //                     'amount': parseFloat($('tr#order_total').find('.oe_currency_value').text().replaceAll(',','')),
    //                     'currencyId': form.data("currency-id"),
    //                     'partnerId': form.data("partner-id"),
    //                     'invoiceId': form.data("invoice-id"),
    //                     'accessToken': form.data("access-token"),
    //                 }
    //                 var values = {
    //                     'payment_option_id': $(checked_radio).data("payment-option-id"),
    //                     'reference_prefix': txContext.referencePrefix !== undefined
    //                         ? txContext.referencePrefix.toString() : null,
    //                     'amount': txContext.amount !== undefined
    //                         ? parseFloat(txContext.amount) : null,
    //                     'currency_id': txContext.currencyId
    //                         ? parseInt(txContext.currencyId) : null,
    //                     'partner_id': parseInt(txContext.partnerId),
    //                     'invoice_id': txContext.invoiceId
    //                         ? parseInt(txContext.invoiceId) : null,
    //                     'flow': "redirect",
    //                     'tokenization_requested': false,
    //                     'is_validation': false,
    //                     'landing_route': form.data("landing-route"),
    //                     'access_token': txContext.accessToken
    //                         ? txContext.accessToken : undefined,
    //                     'csrf_token': core.csrf_token,
    //                 }
    //                 return self._rpc({
    //                     route: $tx_url,
    //                     params: values,
    //                 }).then(function (result) {
    //                     var newform = document.createElement('div');
    //                     var $newform = $(newform)
    //                     $newform.append(result["redirect_form_html"]);
    //                     return {
    //                         amount : $newform.find('input[name="amount"]').val(),
    //                         reference : $newform.find('input[name="invoice_num"]').val(),
    //                         so_reference : $newform.find('input[name="so_reference"]').val(),
    //                         currency_code : $newform.find('input[name="currency_code"]').val(),
    //                         billing_first_name: $newform.find('input[name="billing_first_name"]').val(),
    //                         billing_last_name: $newform.find('input[name="billing_last_name"]').val(),
    //                         billing_phone: $newform.find('input[name="billing_phone"]').val(),
    //                         billing_email: $newform.find('input[name="billing_email"]').val(),
    //                         billing_address_l1: $newform.find('input[name="billing_address_l1"]').val(),
    //                         billing_area1: $newform.find('input[name="billing_area1"]').val(),
    //                         billing_area2: $newform.find('input[name="billing_area2"]').val(),
    //                         billing_zip_code: $newform.find('input[name="billing_zip_code"]').val(),
    //                         billing_country_code: $newform.find('input[name="billing_country_code"]').val(),
    //                         shipping_partner_name: $newform.find('input[name="shipping_partner_name"]').val(),
    //                         shipping_address_l1: $newform.find('input[name="shipping_address_l1"]').val(),
    //                         shipping_area1: $newform.find('input[name="shipping_area1"]').val(),
    //                         shipping_area2: $newform.find('input[name="shipping_area2"]').val(),
    //                         shipping_zip_code: $newform.find('input[name="shipping_zip_code"]').val(),
    //                         shipping_country_code: $newform.find('input[name="shipping_country_code"]').val(),
    //                     };
    //                 });
    //             }
    //         }
    //         return {}
    //     },
    //     checkout_override: function () {
    //         var self = this;
    //         var loader = $('#paypal_express_loader');
    //         paypal.Buttons({
    //             style: self.get_btn_style(),
    //             createOrder: function(data, actions) {
    //                 loader.show();
    //                 return self.order_values().then(function (values){
    //                     loader.hide();
    //                     return actions.order.create({
    //                         payer: get_payer_data(values),
    //                         purchase_units: [{
    //                             amount: {
    //                                 value: values.amount,
    //                                 currency_code: values.currency_code
    //                             },
    //                             description: values.so_reference,
    //                             reference_id: values.reference,
    //                             shipping: get_shipping_data(values),
    //                         }],
    //                     });
    //                 });
    //             },

    //             onApprove: function(data, actions) {
    //                 loader.show();
    //                 return actions.order.capture()
    //                 .then(function (details) {
    //                     self._rpc({
    //                         route: '/paypal/express/checkout/state',
    //                         params: details
    //                     }).then(function(result){
    //                         window.location.href = window.location.origin + result
    //                         loader.hide();
    //                     });
    //                 });
    //             },
    //             onCancel: function (data, actions) {
    //                 loader.show();
    //                 self._rpc({
    //                     route: '/paypal/express/checkout/cancel',
    //                     params: data
    //                 }).then(function(result){
    //                     window.location.href = window.location.origin + result
    //                     loader.hide();
    //                 });
    //             },
    //             onError: function (error) {
    //                 // This is not handle in this module because of two reasons:
    //                 // 1. error object details is not mention in paypal doc.
    //                 // 2. Page close and page unload trigger onError function of Smart Payment Button.
    //                 loader.hide();
    //                 return alert(error);
    //             }
    //         }).render('#mobile-paypal-button');
    //     },
    // });

    // PaymentForm.include({
    //     start: async function () {
    //         await this._super(...arguments);
    //         const $paypalExpressRadio = this.$('input[data-provider="paypal_express"]').attr('checked', true);

    //         const $checkedRadios = this.$('input[name="o_payment_radio"]:checked');
    //         if ($checkedRadios.length === 1) {
    //             const checkedRadio = $checkedRadios[0];
    //             this._displayInlineForm(checkedRadio);
    //             if($checkedRadios.attr('data-provider') == 'paypal_express'){
    //                 $("button[name='o_payment_submit_button']").hide();
    //                 $('#mobile-paypal-button').show();
    //             }else{
    //                 this._enableButton();
    //             }
    //         } else {
    //             this._setPaymentFlow(); // Initialize the payment flow to let acquirers overwrite it
    //         }
    //     },
    //     _onClickPaymentOption: function () {
    //         this._super.apply(this, arguments);
    //         var checked_radio = this.$('input[type="radio"]:checked');
    //         if (checked_radio.length !== 1) {
    //             return;
    //         }
    //         checked_radio = checked_radio[0];
    //         var provider = checked_radio.dataset.provider
    //         if(provider == 'paypal_express'){
    //             $("button[name='o_payment_submit_button']").hide();
    //             $('#mobile-paypal-button').show();
    //         }
    //         else{
    //             $('#mobile-paypal-button').hide();
    //             $("button[name='o_payment_submit_button']").show();
    //         }
    //     },
    // });

    // return publicWidget.registry.MobilePaypalCheckoutButton;
});
