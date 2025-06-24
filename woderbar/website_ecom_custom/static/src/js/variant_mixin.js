odoo.define('website_ecom_custom.VariantMixin', function (require) {
'use strict';

var VariantMixin = require('sale.VariantMixin');
var publicWidget = require('web.public.widget');

require('website_sale.website_sale');

publicWidget.registry.WebsiteSale.include({
    /**
     * Adds the description_sale to the regular _onChangeCombination method
     * @override
     */
    _onChangeCombination: function () {
        this._super.apply(this, arguments);
        if (arguments[2]['description_sale'] && document.querySelector("#tab-description") != null){
            document.querySelector("#tab-description").innerHTML = arguments[2]['description_sale']
        }
    },

});

return VariantMixin;

});
