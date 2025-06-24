odoo.define('pos_sale.PharmacyList', function (require) {
    'use strict';

    const { useState } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class PharmacyList extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click-order', this._onClickOrder);
            this.state = useState({ highlightedOrder: this.props.initHighlightedOrder || null });
        }
        get highlightedOrder() {
            return this.state.highlightedOrder;
        }
        _onClickOrder({ detail: order }) {
            this.state.highlightedOrder = order;
        }
    }
    PharmacyList.template = 'PharmacyList';

    Registries.Component.add(PharmacyList);

    return PharmacyList;
});
