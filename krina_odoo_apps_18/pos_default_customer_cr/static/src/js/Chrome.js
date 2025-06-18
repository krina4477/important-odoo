/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
        add_new_order() {
        const order = super.add_new_order(...arguments);
        if (this.config.customer_id) {
            order.set_partner(this.config.customer_id)
            }
        return order;
    },

    },
);
