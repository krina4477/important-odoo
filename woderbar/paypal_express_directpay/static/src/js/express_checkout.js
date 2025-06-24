/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('wk_paypal_express_custom.express_checkout_custom', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var page_url = window.location.href
    var publicWidget = require('web.public.widget');
    const { loadJS } = require('@web/core/assets');
    var core = require('web.core');
    var type;
    if (page_url.indexOf("/shop/cart") > -1){
        type = "cart"
    }
    else if (page_url.indexOf("/shop/payment") > -1){
      type = "payment"
    }
    else if (page_url.indexOf("/shop/") > -1){
        type = "product"
    }


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

    publicWidget.registry.PaypalCheckoutButton = publicWidget.Widget.extend({
            selector: '#paypal-button',
            willStart: function () {
                if (type=="cart" || type=="product"){

                var self = this;
                return this._super.apply(this, arguments).then(function () {
                    return self._rpc({
                        route: '/paypal/express/checkout/url',
                        params: {}
                    }).then(function(url){
                        if(url){
                            return ajax.loadJS(url).then(function(){
                                self.checkout_override();
                            });
                        }
                    });
                });}
                return this._super.apply(this, arguments)
            },
            get_btn_style: function(){
                if (type=="cart" || type=="product"){
                    var b_style = {
                        color:   'gold',
                        shape:   'rect',
                        label:   'checkout',
                        size: 'small',
                        height: 34,
                        tagline: false,
                    }
                    if (type=="cart"){
                        $("#paypal-button").addClass("cart_paypal_button mr-1")
                    }
                    else if (type == "product"){
                            b_style["height"] = 40;
                            b_style["size"] = 'small';
                            $("#paypal-button").addClass("pro_paypal_button")
                    }
                    return b_style

                }else{
                    return this._super.apply(this, arguments);
                }
            },
            get_transaction: function(result){
              var self = this;
              return self._rpc({
                      route: '/get/paypal/acquirer/details',
                      params : result,
                      }).then(function (result) {
                          var acquirer_id = result.acquirer_id
                          var values = {
                                      'acquirer_id': parseInt(acquirer_id),
                                      'public_paypal_checkout':true,
                                      'sale_order' : result.sale_order,
                                      'currency_id' : result.currency_id,
                                      'partner_id'   : result.partner_id,
                                      'flow'          : result.flow,
                                      'tokenization_requested' : result.tokenization_requested,
                                      'landing_route': result.landing_route,
                                      'access_token': result.access_token,
                                        'csrf_token': core.csrf_token,
                                        'payment_option_id': parseInt(acquirer_id),
                                        'amount':parseFloat(result.amount),
                                    }
                          return self._rpc({
                                  route: '/shop/payment/transaction/'.concat(result.sale_order),
                                  params: values,
                                  }).then(function (result) {
                                    var newForm = document.createElement('div');
                                        newForm.innerHTML = result["redirect_form_html"];
                                        return {
                                              amount : parseFloat($(newForm).find('input[name="amount"]').val()).toFixed(2),
                                              reference : $(newForm).find('input[name="invoice_num"]').val(),
                                              currency_code : $(newForm).find('input[name="currency_code"]').val(),
                                              billing_first_name: $(newForm).find('input[name="billing_first_name"]').val(),
                                              billing_last_name: $(newForm).find('input[name="billing_last_name"]').val(),
                                              billing_phone: $(newForm).find('input[name="billing_phone"]').val(),
                                              billing_email: $(newForm).find('input[name="billing_email"]').val(),
                                              billing_address_l1: $(newForm).find('input[name="billing_address_l1"]').val(),
                                              billing_area1: $(newForm).find('input[name="billing_area1"]').val(),
                                              billing_area2: $(newForm).find('input[name="billing_area2"]').val(),
                                              billing_zip_code: $(newForm).find('input[name="billing_zip_code"]').val(),
                                              billing_country_code: $(newForm).find('input[name="billing_country_code"]').val(),
                                              shipping_partner_name: $(newForm).find('input[name="shipping_partner_name"]').val(),
                                              shipping_address_l1: $(newForm).find('input[name="shipping_address_l1"]').val(),
                                              shipping_area1: $(newForm).find('input[name="shipping_area1"]').val(),
                                              shipping_area2: $(newForm).find('input[name="shipping_area2"]').val(),
                                              shipping_zip_code: $(newForm).find('input[name="shipping_zip_code"]').val(),
                                              shipping_country_code: $(newForm).find('input[name="shipping_country_code"]').val(),
                                      }
                                      })
                          })
            },
            create_order: function(){
                var self = this;
                var product_id = parseInt($('#paypal-button').closest('.js_product').find('input[name="product_id"]').val());
                var add_qty = parseInt($('#paypal-button').closest('.js_product').find('input[name="add_qty"]').val());
                var csrf_token = parseInt($('#paypal-button').closest('.js_product').find('input[name="csrf_token"]').val());
                var values = {
                    'product_id': product_id,
                    'add_qty':  add_qty,
                    'csrf_token':csrf_token,
                            }
                return self._rpc({
                        route: '/get/product/order/details',
                        params: values,
                        }).then(function (result) {
                            return result
                            })
            },

            order_values: function () {
                var self = this;
                var page_url = window.location.href
                if (page_url.indexOf("/shop/payment") > -1){
                    return this._super.apply(this, arguments);
                }
                if(type=="product"){

                    return self.create_order().then(function(result){
                      return self.get_transaction(result)
                    })
                }else{
                  return self.get_transaction()
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
                    // This is not handle in this module because of two reasons:
                    // 1. error object details is not mention in paypal doc.
                    // 2. Page close and page unload trigger onError function of Smart Payment Button.
                    loader.hide();
                    return alert(error);
                }
            }).render('#paypal-button');
        },


});
});
