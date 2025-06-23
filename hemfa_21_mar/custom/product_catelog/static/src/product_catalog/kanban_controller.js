/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class ProductCatalogKanbanController extends KanbanController {

    setup() {
        super.setup();
        this.action = useService("action");
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        if (this.props.context.product_catalog_order_model == 'inventory.adjustment.template.new' ) {
            this.orderId = this.props.context.inventory_id;
        }
        else if (this.props.context.product_catalog_order_model == 'account.move' ) {
                this.orderId = this.props.context["move_id."];
        }
        else {

            if (this.props.context.product_catalog_order_model == 'custom.warehouse.stock.request'){
                this.orderId = this.props.context.stock_request_id;
            }
            else{
                if (this.props.context.product_catalog_order_model == 'stock.picking'){
                    this.orderId = this.props.context["picking_id "];
                }
                else{
                     this.orderId = this.props.context.order_id;
                }


            }
        }
        this.orderResModel = this.props.context.product_catalog_order_model;

        onWillStart(async () => this._defineButtonContent());
    }

    // Force the slot for the "Back to Quotation" button to always be shown.
    get canCreate() {
        return true;
    }

    async _defineButtonContent() {
        var self = this
        // Define the button's label depending of the order's state.

        if (self.props.context.product_catalog_order_model == 'stock.picking' ) {

            const orderStateInfo = await self.orm.searchRead(
                self.orderResModel, [["id", "=", self.orderId]], []
            );

            const orderIsQuotation = ["draft", "sent"].includes(orderStateInfo[0]);
            if (orderIsQuotation) {
                self.buttonString = _t("Back to Stock");
            } else {
                self.buttonString = _t("Back to Stock");
            }
            return
        }

        if (self.props.context.product_catalog_order_model == 'inventory.adjustment.template.new' ) {
            const orderStateInfo = await self.orm.searchRead(
                self.orderResModel, [["id", "=", self.orderId]], []
            );
            const orderIsQuotation = ["draft", "sent"].includes(orderStateInfo[0]);
            if (orderIsQuotation) {
                self.buttonString = _t("Back to Inventory Adjustment");
            } else {
                self.buttonString = _t("Back to Inventory Adjustment");
            }
            return
        }

        if (self.props.context.product_catalog_order_model == 'account.move' ) {
            const orderStateInfo = await self.orm.searchRead(
                self.orderResModel, [["id", "=", self.orderId]], []
            );
            const orderIsQuotation = ["draft", "sent"].includes(orderStateInfo[0]);
            if (orderIsQuotation) {
                self.buttonString = _t("Back to Invoice");
            } else {
                self.buttonString = _t("Back to Invoice");
            }
        }
        else {
            const orderStateInfo = await self.orm.searchRead(
                self.orderResModel, [["id", "=", self.orderId]], ["state"]
            );
            const orderIsQuotation = ["draft", "sent"].includes(orderStateInfo[0].state);

             if (self.props.context.product_catalog_order_model == 'custom.warehouse.stock.request' ) {

                if (orderIsQuotation) {
                        self.buttonString = _t("Back to Warehouse Stock");
                } else {
                       self.buttonString = _t("Back to Warehouse Stock");
                }


             }
             else if (self.props.context.product_catalog_order_model == 'purchase.order' ) {

                if (orderIsQuotation) {
                        self.buttonString = _t("Back to Purchase Order");
                } else {
                       self.buttonString = _t("Back to Purchase Order");
                }


             }
             else{
                 if (orderIsQuotation) {
                    self.buttonString = _t("Back to Quotation");
                } else {
                    self.buttonString = _t("Back to Order");
                }
             }
        }


    }

    async backToQuotation() {
        // Restore the last form view from the breadcrumbs if breadcrumbs are available.
        // If, for some weird reason, the user reloads the page then the breadcrumbs are
        // lost, and we fall back to the form view ourselves.
        if (this.env.config.breadcrumbs.length > 1) {
            await this.action.restore();
        } else {
            await this.action.doAction({
                type: "ir.actions.act_window",
                res_model: this.orderResModel,
                views: [[false, "form"]],
                view_mode: "form",
                res_id: this.orderId,
            });
        }
    }

    async ClearAllOrders () {
        const orderLinesInfo = this.rpc("/product/catalog/clear_orders", {
            order_id: Number(this.orderId),
            res_model: this.orderResModel,
        });
        await this.model.root.load()
        await this.render(true);
    }
}
