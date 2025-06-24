odoo.define('website_sale_tracking_wb.tracking', function (require) {
    "use strict";

    const websiteSaleTrackingAlternative = require('website_sale_tracking_base.tracking');

    websiteSaleTrackingAlternative.include({

        start: function (ev) {
            let self = this;
            // purchase
            const $confirmation = this.$('div#subtotal_excluding_delivery');
            if ($confirmation.length) {
                if (self.trackingIsLogged()) { console.log('[Tracking] Purchase (Custom)') }
                this.trackingExecuteEvent({
                    event_type: 'purchase',
                    order_id: parseInt($confirmation.data('order-id'), 10),
                });
            }
            return this._super.apply(this, arguments);
        },
    });
});
