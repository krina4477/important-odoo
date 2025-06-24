/** @odoo-module **/

import publicWidget from "web.public.widget";
import "website_sale.website_sale";
var wSaleUtils = require('website_sale.utils');
const cartHandlerMixin = wSaleUtils.cartHandlerMixin;

publicWidget.registry.WebsiteSale.include({

    events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events, {
        'click button.update_cart_onchange': '_onCustomCartUpdate1',
    }),

    init: function () {
        this._super.apply(this, arguments);
    },

    _changeCustomCartQuantity: function ($input, value, $dom_optional, line_id, productIDs) {

        _.each($dom_optional, function (elem) {
            $(elem).find('.js_quantity').text(value);
            productIDs.push($(elem).find('span[data-product-id]').data('product-id'));
        });
        $input.data('update_change', true);

        this._rpc({
            route: "/shop/cart/update_json",
            params: {
                line_id: line_id,
                product_id: parseInt($input.data('product-id'), 10),
                set_qty: value
            },
        }).then(function (data) {
            $input.data('update_change', false);
            var check_value = parseInt($input.val() || 0, 10);
            if (isNaN(check_value)) {
                check_value = 1;
            }
            if (value !== check_value) {
                $input.trigger('change');
                return;
            }
            if (!data.cart_quantity) {
                return window.location = '/shop/cart';
            }
            $input.val(data.quantity);
            $('.js_quantity[data-line-id=' + line_id + ']').val(data.quantity).text(data.quantity);

            wSaleUtils.updateCartNavBar(data);
            wSaleUtils.showWarning(data.warning);
        });
    },

    _onCustomCartUpdate1: function (ev) {
        var tbody = $(ev.currentTarget).closest('tr').parent();
        let i = 0
        while (i < tbody.find('tr').length - 1) {
            var tr = $(tbody.find('tr')[i])
            var $input = $(tr.find('input'));

            var value = parseInt($input.val() || 0, 10);

            if (isNaN(value)) {
                value = 1;
            }

            var $dom = $input.closest('tr');
            var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
            var line_id = parseInt($input.data('line-id'), 10);
            var productIDs = [parseInt($input.data('product-id'), 10)];
            this._changeCustomCartQuantity($input, value, $dom_optional, line_id, productIDs);
            i++;
        }
    },

});
