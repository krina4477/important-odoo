/** @odoo-module */
import { useSubEnv } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";
import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { ProductCatalogOrderLine } from "./order_line/order_line";
const { xml, useState, onWillUpdateProps } = owl;

export class ProductCatalogKanbanRecord extends KanbanRecord {

    setup() {
        super.setup();
        this.rpc = useService("rpc");
        const productCatalogData = this.props.record.productCatalogData || {};


        this.props.record.productCatalogData = useState({
            price: productCatalogData.price || 0,
            quantity: productCatalogData.quantity || 0,
            deliveredQty: productCatalogData.deliveredQty || 0,
            productType: productCatalogData.productType || "",
        });

        this.debouncedUpdateQuantity = useDebounced(this._updateQuantity, 500, {
            execBeforeUnmount: true,
        });

        if (this?.props?.record?.context?.product_catalog_order_model == 'account.move') {
            this.move_id = this.props.record.context["move_id."]
        }
//        else {
//            this.move_id = this.props.record.context.product_catalog_order_id
//        }

        if (this?.props?.record?.context?.product_catalog_order_model == 'stock.picking') {
            this.move_id = this.props.record.context["picking_id "]
        }
        else {
            this.move_id = this.props.record.context.product_catalog_order_id
        }


        useSubEnv({
            currencyId: this.props.record.context.product_catalog_currency_id,
            orderId: this.move_id,
            orderResModel: this.props.record.context.product_catalog_order_model,
            digits: this.props.record.context.product_catalog_digits,
            displayUoM: this.props.record.context.display_uom,
            precision: this.props.record.context.precision,
            productId: this.props.record.resId,
            addProduct: this.addProduct.bind(this),
            removeProduct: this.removeProduct.bind(this),
            increaseQuantity: this.increaseQuantity.bind(this),
            setQuantity: this.setQuantity.bind(this),
            decreaseQuantity: this.decreaseQuantity.bind(this),
        });

    }
    get orderLineComponent() {
        return ProductCatalogOrderLine;
    }

    get productCatalogData() {
        return this.props.record.productCatalogData;
    }

    async onGlobalClick(ev) {
        // avoid a concurrent update when clicking on the buttons (that are inside the record)
        if (ev.target.closest(".o_product_catalog_cancel_global_click")) {
            return;
        }
        if (this.productCatalogData.quantity === 0) {
            this.addProduct();
        } else {
            this.increaseQuantity();
        }
        await this.render(true);
    }

    //--------------------------------------------------------------------------
    // Data Exchanges
    //--------------------------------------------------------------------------

    async _updateQuantity() {
        const price = await this._updateQuantityAndGetPrice();
        this.productCatalogData.price = parseFloat(price);
    }

    _updateQuantityAndGetPrice() {
        return this.rpc("/product/catalog/_update_order_line_globle_click", this._getUpdateQuantityAndGetPrice());
    }

    _getUpdateQuantityAndGetPrice() {
        return {
            order_id: this.env.orderId,
            product_id: this.env.productId,
            quantity: this.productCatalogData.quantity,
            res_model: this.env.orderResModel,
        }

    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    updateQuantity(quantity) {
        if (this.env.orderResModel !== "sale.order" || this.productCatalogData.productType == "service") {
            if (this.productCatalogData.readOnly) {
                return;
            }
            this.productCatalogData.quantity = quantity || 0;
            this.debouncedUpdateQuantity();
        } else if (
            this.productCatalogData.quantity === this.productCatalogData.deliveredQty &&
            quantity < this.productCatalogData.quantity
        ) {
            // This condition is only triggered when the product was already at the minimum quantity
            // possible, as stated in the sale_stock module, then the user inputs a quantity lower
            // than this limit, in this case we need the record to forcefully update the record.
            this.props.record.load();
            this.props.record.model.notify();
        } else {
            quantity = Math.max(quantity, this.productCatalogData.deliveredQty);
            if (this.productCatalogData.readOnly) {
                return;
            }
            this.productCatalogData.quantity = quantity || 0;
            this.debouncedUpdateQuantity();
        }
    }

    /**
     * Add the product to the order
     */
    addProduct(qty=1) {
        this.updateQuantity(qty);
    }

    /**
     * Remove the product to the order
     */
    removeProduct() {
        this.updateQuantity(0);
    }

    /**
     * Increase the quantity of the product on the order line.
     */
    async increaseQuantity(qty=1) {
        this.updateQuantity(this.productCatalogData.quantity + qty);
        await this.render(true);

    }

    /**
     * Set the quantity of the product on the order line.
     *
     * @param {Event} event
     */
    setQuantity(event) {
        this.updateQuantity(parseFloat(event.target.value));
    }

    /**
     * Decrease the quantity of the product on the order line.
     */
    async decreaseQuantity() {
        this.updateQuantity(parseFloat(this.productCatalogData.quantity - 1));
        await this.render(true);
    }
}

ProductCatalogKanbanRecord.components = {
    ...KanbanRecord.components,
    ProductCatalogOrderLine,
};
ProductCatalogKanbanRecord.template = "ProductCatalogKanbanRecord";