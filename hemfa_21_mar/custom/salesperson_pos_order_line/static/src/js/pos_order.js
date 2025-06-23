odoo.define('salesperson_pos_order_line.PosOrder', function (require) {
    "use strict";

    const { PosGlobalState, Order, Orderline, Payment } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosOrderLine = (Order) => class PosOrderLine extends Order {

        constructor(obj, options) {
            super(obj, options)
            if (options.json) {
                this.salesperson = options.json.salesperson;
            }
        }
        /**
         * Initializes the `SalesPersonOrderline` instance from JSON.
         *
         * @param {Object} json - The JSON object to initialize from.
         */
        init_from_JSON(json) {
            super.init_from_JSON(json)
            this.salesperson = json.salesperson;
        }
        /**
         * Exports the `SalesPersonOrderline` instance as a JSON object.
         *
         * @returns {Object} - The JSON object that represents the order line.
         */
        export_as_JSON() {
            if (this.salesperson) {
                var sales_user_id = this.salesperson[0]
            } else {
                var sales_user_id = ''
            }
            console.log("=============salesperssssssss=========", sales_user_id);
            return _.extend(super.export_as_JSON(...arguments), {
                sales_user_id: sales_user_id
            })
        }

    }

    Registries.Model.extend(Order, PosOrderLine);
});

