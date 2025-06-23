/** @odoo-module */
import { Component } from "@odoo/owl";
import { formatFloat, formatMonetary } from "@web/views/fields/formatters";
const { xml, useState , onWillUpdateProps } = owl;
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

export class ProductCatalogOrderLine extends Component {

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    isInOrder() {
        return this.props.quantity !== 0;
    }

    get disableRemove() {
        return this.props.quantity === this.props.deliveredQty;
    }

    get disabledButtonTooltip() {
        if (this.disableRemove) {
            return _t("The ordered quantity cannot be decreased below the amount already delivered. Instead, create a return in your inventory.");
        }
        return super.disabledButtonTooltip;
    }

    get price() {
        const { currencyId, digits } = this.env;
        return formatMonetary(this.props.price, { currencyId, digits });
    }

    get quantity() {
        const digits = [false, this.env.precision];
        const options = { digits, decimalPoint: ".", thousandsSep: "" };
        return parseFloat(formatFloat(this.props.quantity, options));
    }
}

ProductCatalogOrderLine.template = "product_catelog.ProductCatalogOrderLine";
ProductCatalogOrderLine.props = {
    productId: { type: Number, optional: true},
    quantity:{ type: Number, optional: true},
    price:  { type: Number, optional: true},
    productType:{ type: String, optional: true } ,
    readOnly: { type: Boolean, optional: true },
    warning: { type: String, optional: true},
    deliveredQty: { type: Number, optional: true},
};

