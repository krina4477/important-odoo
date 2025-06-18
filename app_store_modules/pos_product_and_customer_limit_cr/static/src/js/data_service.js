import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import DevicesSynchronisation from "@point_of_sale/app/store/devices_synchronisation";

patch(PosStore.prototype, {
    async afterProcessServerData() {
        const paidUnsyncedOrderIds = this.models["pos.order"]
            .filter((order) => order.isUnsyncedPaid)
            .map((order) => order.id);

        if (paidUnsyncedOrderIds.length > 0) {
            this.addPendingOrder(paidUnsyncedOrderIds);
        }

        // Adding the not synced paid orders to the pending orders
        const openOrders = this.data.models["pos.order"].filter((order) => !order.finalized);
        this.syncAllOrders();

        if (!this.config.module_pos_restaurant) {
            this.selectedOrderUuid = openOrders.length
                ? openOrders[openOrders.length - 1].uuid
                : this.add_new_order().uuid;
        }

        this.markReady();
        this.showScreen(this.firstScreen);
        await this.deviceSync.readDataFromServer();
        this.deviceSync.loadProducts();
    }
});
patch(DevicesSynchronisation.prototype, {
    async loadProducts() {
        if(this.pos.config.limited_products_loading && this.pos.config.product_load_background){
            let product_model = 'product.product';
            let products = [];
            let data = {};
            products = await this.pos.data.call("product.product", "pos_load_data", [
                [],
                this.pos.config.current_session_id.id,
                this.pos.config.limited_product_count,
            ]);
            for (const [model, values] of Object.entries(products)) {
                data[model] = values.data;
            }
            this.models.loadData(data, ['product.product'], true, true);
        }
        if(this.pos.config.limited_partners_loading && this.pos.config.partner_load_background){
            let product_model = 'res.partner';
            let customers = [];
            let data = {};

            customers = await this.pos.data.call("res.partner", "pos_load_data", [
                [],
                this.pos.config.id,
                this.pos.config.limited_partner_count,
            ]);
            for (const [model, values] of Object.entries(customers)) {
                data[model] = values.data;
            }
            this.models.loadData(data, ['res.partner'], true, true);
        }
    }
});
