// /** @odoo-module */
// import { ProductCatalogKanbanRecord } from "@product_catelog/product_catalog/kanban_record";
// // import { ProductCatalogSaleOrderLine } from "@product_catelog/product_catalog/search/sale_order_line";
// import { patch } from "@web/core/utils/patch";
// import { ProductCatalogOrderLine } from "@product_catelog/product_catalog/order_line/order_line";

// patch(ProductCatalogKanbanRecord.prototype, 'sale_order', {
//     get orderLineComponent() {
//         if (this.env.orderResModel === "sale.order") {
//             return ProductCatalogOrderLine;
//         }
//         return super.orderLineComponent;
//     },
// });
