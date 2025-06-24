odoo.define('pos_sale.PharmacyOrderRow', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');


    class PharmacyOrderRow extends PosComponent {
        get order() {
            return this.props.order;
        }
        get highlighted() {
            const highlightedOrder = this.props.highlightedOrder;
            return !highlightedOrder ? false : highlightedOrder.backendId === this.props.order.backendId;
        }

        // Column getters //

        get name() {
            return this.order.name;
        }
        get appointment_date() {
            return moment(this.order.appointment_date).format('YYYY-MM-DD hh:mm A');
        }
        get patient_id() {
            return this.order.patient_id[1];

        }
        get doctor_id() {
            return this.order.doctor_id[1];
        }
        get doctor_id() {
            return this.order.doctor_id[1];
        }
       get state() {
            let state_mapping = {
              'draft': this.env._t('Draft'),
              'pending': this.env._t('Pending'),
              'confirm': this.env._t('Confirm'),
              'sent': this.env._t('Done'),
              'cancel': this.env._t('Cancelled'),
            };

            return state_mapping[this.order.state];
        }

    }
    PharmacyOrderRow.template = 'PharmacyOrderRow';

    Registries.Component.add(PharmacyOrderRow);

    return PharmacyOrderRow;
});

