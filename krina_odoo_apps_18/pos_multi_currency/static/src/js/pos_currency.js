/** @odoo-module */

odoo.define('pos_multi_currency.CurrencyHandler', function(require) {
    'use strict';

    const models = require('point_of_sale.models');

    models.load_fields('pos.config', ['enable_multi_currency', 'currency_id']);
    models.load_fields('product.pricelist', ['currency_id']);

    const _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
            _super_order.initialize.apply(this, arguments);
            this.currency = this.pos.config.currency_id;
        },
        get_currency: function() {
            return this.currency;
        }
    });
});