odoo.define('website_ecom_custom.payment_wonderbar', function (require) {
'use strict';

    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    publicWidget.registry.PaymentWonderbar = publicWidget.Widget.extend({
        selector: '.payment_wonderbar_div',
        events: {
            'click a.delivery_edit': '_onClickDeliveryEdit',
            'click a.carrier_edit': '_onClickCarrierEdit',

            'change input#same_delivery_input': '_onClickSameDelivery',

            'click .delivery_address_btn a': '_onClickAddressSubmit',
            'click .delivery_method_btn a': '_onClickDeliveryMethodSubmit',
        },

//        async start() {
//            await this._super(...arguments);
//            $('.delivery_edit').hide();
//            $('.str_address').hide();
//            $('#shipping_and_billing').show();
//            $('.str_options').hide();
//            $('.carrier_edit').hide();
//            $('#delivery_carrier').hide();
//            $('.str_payment').hide();
//            $('#payment_and_method_body').hide();
//        },

        init: function (parent, options) {
            this._super.apply(this, arguments);

            $('.delivery_edit').show();
            $('.str_address').show();
            $('#shipping_and_billing').hide();
            $('.str_options').hide();
            $('.carrier_edit').hide();
            $('#delivery_carrier').show();
            $('#payment_and_method_body').show();
            $('.c_activate').removeClass('c_activate');
            $('#delivery_and_carrier .one_count').addClass('c_activate');
        },

        _onClickDeliveryEdit(ev) {
            ev.preventDefault();
            $('.delivery_edit').hide();
            $('.str_address').hide();
            $('#shipping_and_billing').show();
            $('.carrier_edit').hide();
            $('.str_options').show();
            $('#delivery_carrier').hide();
            $('#payment_and_method_body').hide();
            $('.c_activate').removeClass('c_activate');
            $('#address_on_payment .one_count').addClass('c_activate');
        },
        _onClickCarrierEdit(ev) {
            ev.preventDefault();
            $('.delivery_edit').show();
            $('.str_address').show();
            $('#shipping_and_billing').hide();
            $('.carrier_edit').hide();
            $('.str_options').hide();
            $('#delivery_carrier').show();
            $('#payment_and_method_body').hide();
            $('.c_activate').removeClass('c_activate');
            $('#delivery_and_carrier .one_count').addClass('c_activate');
        },

        _onClickSameDelivery(ev) {
            ev.preventDefault();
            let self = this,
            $target = $(ev.currentTarget);
            if($target.is(':checked')){
                $('.billing_address_tag').hide();
            }else{
                $('.billing_address_tag').show();
            }
        },

        _onClickAddressSubmit(ev) {
            ev.preventDefault();
            var self = this;
            var is_invalid_input = false;
            var same_billing_address = true;
            var delivery_address_vals = {};
            var billing_address_vals = {};
            _.each($('.delivery_address .s_website_form_field input'), function(e){
                if($(e).val() || $(e).attr('name') == 'street2'){
                    $(e).removeClass('is-invalid');
                    delivery_address_vals[$(e).attr('name')] = $(e).val() || '';
                }else{
                    is_invalid_input = true;
                    $(e).addClass('is-invalid');
                }
            });
            if($('.delivery_address .s_website_form_field select').val()){
                var name = $('.delivery_address .s_website_form_field select').attr('name')
                var value = $('.delivery_address .s_website_form_field select').val()
                delivery_address_vals[name] = parseInt(value);
            }
            _.each($('.email_address .s_website_form_field input'), function(e){
                if($(e).val() || $(e).attr('name') == 'phone'){
                    $(e).removeClass('is-invalid');
                    delivery_address_vals[$(e).attr('name')] = $(e).val() || '';
                }else{
                    is_invalid_input = true;
                    $(e).addClass('is-invalid');
                }
            });
            if(!$('input#same_delivery_input').is(':checked')){
                same_billing_address = false;
                _.each($('.billing_address .s_website_form_field input'), function(e){
                    if($(e).val() || $(e).attr('name') == 'street2'){
                        $(e).removeClass('is-invalid');
                        billing_address_vals[$(e).attr('name')] = $(e).val() || '';
                    }else{
                        is_invalid_input = true;
                        $(e).addClass('is-invalid');
                    }
                });
                if($('.billing_address .s_website_form_field select').val()){
                    var name = $('.billing_address .s_website_form_field select').attr('name')
                    var value = $('.billing_address .s_website_form_field select').val()
                    billing_address_vals[name] = parseInt(value);
                }
                _.each($('.email_address .s_website_form_field input'), function(e){
                    if($(e).val() || $(e).attr('name') == 'phone'){
                        $(e).removeClass('is-invalid');
                        billing_address_vals[$(e).attr('name')] = $(e).val() || '';
                    }else{
                        is_invalid_input = true;
                        $(e).addClass('is-invalid');
                    }
                });
            }
            if(is_invalid_input){
                location.reload()
            }else{
                ajax.jsonRpc(
                    '/sale/order/update/address',
                    'call', 
                    {
                        'order_id': parseInt($('input[name="current_order_id"]').val()),
                        'delivery_address_vals': delivery_address_vals,
                        'billing_address_vals': billing_address_vals,
                        'same_billing_address': same_billing_address,
                    }
                ).then(function (result) {
                    $('.delivery_edit').show();
                    $('.str_address').show();
                    $('#shipping_and_billing').hide();
                    $('.str_options').hide();
                    $('.carrier_edit').hide();
                    $('#delivery_carrier').show();
                    $('#payment_and_method_body').hide();
                    $('.c_activate').removeClass('c_activate');
                    $('#delivery_and_carrier .one_count').addClass('c_activate');
                    location.reload()
                }).guardedCatch(function (error) {
                    self.displayNotification({
                        message: _t(error.message.data.message),
                        type: 'warning',
                        sticky: true,
                    });
                });
            }
            
        },
        _onClickDeliveryMethodSubmit(ev) {
            ev.preventDefault();
            $('.delivery_edit').show();
            $('.str_address').show();
            $('#shipping_and_billing').hide();
            $('.carrier_edit').show();
            $('.str_options').show();
            $('#delivery_carrier').hide();
            $('#payment_and_method_body').show();
            $('.c_activate').removeClass('c_activate');
            $('#payment_and_method .one_count').addClass('c_activate');
        },


    });
});
