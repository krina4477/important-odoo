/** @odoo-module */
import { KanbanModel } from "@web/views/kanban/kanban_model";
import { useBus, useService } from "@web/core/utils/hooks";
import { SearchBar } from "@web/search/search_bar/search_bar";
import { patch } from "@web/core/utils/patch";

patch(SearchBar.prototype, 'SearchBar_Barcode', {
    onSearchInput(ev) {
        const query = ev.target.value;
        this.env.searchModel.barcode = Number(query);
        if (query.trim()) {
            this.computeState({ query, expanded: [], focusedIndex: 0, subItems: [] });
        } else if (this.items.length) {
            this.resetState();
        }
    }

})


class ProductCatalogRecord extends KanbanModel.Record {

    setup(params, state) {
        if (this.parentRecord) {
            this.productCatalogData = this.parentRecord.productCatalogData;
            delete this.parentRecord.productCatalogData;
        }
        super.setup(params, state);
    }
}

export class ProductCatalogKanbanModel extends KanbanModel {
    async setup(params) {
        super.setup(...arguments);
        var self = this
        this.check = false
        self.object_list = []


                useBus(self.env.searchModel, "update", (ev) => {

                console.log("===================d'd'd'd'd'd'd'd'd''d'd'd");
            if (self.env.searchModel.facets.length === 1) {
                self.check = true;
                self.barcode_cutom = self.env.searchModel.barcode;
            } else {
                self.check = false;
            }
        });
    }

    async load(params = {}) {
        const rootParams = { ...this.rootParams, ...params };
        const result = await super.load(...arguments);
        var self = this


        const loadParams = { ...this.__bm_load_params__ };

        if ("resId" in params) {
            loadParams.res_id = params.resId || undefined;
        }
        if ("context" in params) {
            loadParams.context = params.context;
        }
        if (!params.isMonoRecord && !params.groupBy.length && params.context.product_catalog_order_model == 'inventory.adjustment.template.new') {

            const orderLinesInfo = await this.rpc("/product/catalog/order_lines_info", {
                order_id: params.context.inventory_id,
                product_ids: self.root.records.map((rec) => rec.resId),
                res_model: params.context.product_catalog_order_model,
            });

            for (const record of self.root.records) {

                if (self.check) {

                    self.removeFacet(self.env.searchModel.facets[self.env.searchModel.facets.length - 1]);
                    record.productCatalogData = orderLinesInfo[record.resId];
                    record.productCatalogData.quantity = record.productCatalogData.quantity + 1
                    self.check = false

                    self.rpc("/product/catalog/update_order_line_info", {
                        order_id: params.context.inventory_id,
                        product_id: record.resId,
                        quantity: record.productCatalogData.quantity,
                        res_model: params.context.product_catalog_order_model,
                        barcode_cutom : self.barcode_cutom
                    });
//
//                    for (const update_record of self.root.records) {
//                        if (update_record.resId === record.resId) {
//                            Object.assign(update_record, record);
//                        }
//                    }
//
//                    self.object_list = self.root.records;

                }
                else {
                    if (self.object_list.length == 0) {
                        record.productCatalogData = orderLinesInfo[record.resId];
                        self.check = false
                    }
                    else {

                        if (record.resId == self.object_list[0].resId) {
                            record.productCatalogData = self.object_list[0].productCatalogData;
                            self.object_list = [];
                            self.check = false
                        }
                        else {
                            record.productCatalogData = orderLinesInfo[record.resId];
                            self.check = false
                        }
                    }
                }
                self.check = false
            }
        }
        else if (!params.isMonoRecord && params.context.product_catalog_order_model == 'account.move'){

            const orderLinesInfo = await self.rpc("/product/catalog/order_lines_info", {
                order_id: params.context["move_id."],
                product_ids: self.root.records.map((rec) => rec.resId),
                res_model: params.context.product_catalog_order_model,
            });

            for (const record of self.root.records) {

                if (self.check) {

                    self.removeFacet(self.env.searchModel.facets[self.env.searchModel.facets.length - 1]);
                    record.productCatalogData = orderLinesInfo[record.resId];
                    record.productCatalogData.quantity = record.productCatalogData.quantity + 1
                    self.check = false

                    self.rpc("/product/catalog/update_order_line_info", {
                        order_id: params.context["move_id."],
                        product_id: record.resId,
                        quantity: record.productCatalogData.quantity,
                        res_model: params.context.product_catalog_order_model,
                        barcode_cutom : self.barcode_cutom
                    });

//                    for (const update_record of self.root.records) {
//                        if (update_record.resId === record.resId) {
//                            Object.assign(update_record, record);
//                        }
//                    }
//                    self.object_list = self.root.records;

                }else {
                    if (self.object_list.length == 0) {
                        record.productCatalogData = orderLinesInfo[record.resId];
                        self.check = false
                    }
                    else {

                        if (record.resId == self.object_list[0].resId) {
                            record.productCatalogData = self.object_list[0].productCatalogData;
                            self.object_list = [];
                            self.check = false
                        }
                        else {
                            record.productCatalogData = orderLinesInfo[record.resId];
                            self.check = false
                        }
                    }
                }
                self.check = false
            }
        }
        else {
              if (!params.isMonoRecord && !params.groupBy.length && params.context.product_catalog_order_model == 'custom.warehouse.stock.request'){

                const orderLinesInfo = await this.rpc("/product/catalog/order_lines_info", {
                    order_id: params.context.stock_request_id,
                    product_ids: self.root.records.map((rec) => rec.resId),
                    res_model: params.context.product_catalog_order_model,
                });

                for (const record of self.root.records) {

                    if (self.check) {

                        self.removeFacet(self.env.searchModel.facets[self.env.searchModel.facets.length - 1]);
                        record.productCatalogData = orderLinesInfo[record.resId];
                        record.productCatalogData.quantity = record.productCatalogData.quantity + 1
                        self.check = false

                        self.rpc("/product/catalog/update_order_line_info", {
                            order_id: params.context.stock_request_id,
                            product_id: record.resId,
                            quantity: record.productCatalogData.quantity,
                            res_model: params.context.product_catalog_order_model,
                            barcode_cutom : self.barcode_cutom
                        });

//                        for (const update_record of self.root.records) {
//                            if (update_record.resId === record.resId) {
//                                Object.assign(update_record, record);
//                            }
//                        }
//
//                        self.object_list = self.root.records;

                    }else {
                        if (self.object_list.length === 0) {
                            record.productCatalogData = orderLinesInfo[record.resId];
                            self.check = false
                        }
                        else {

                            if (record.resId === self.object_list[0].resId) {
                                record.productCatalogData = self.object_list[0].productCatalogData;
                                self.object_list = [];
                                self.check = false
                            }
                            else {
                                record.productCatalogData = orderLinesInfo[record.resId];
                                self.check = false
                            }
                        }
                    }
                    self.check = false
                }

              }else{

                  if (!params.isMonoRecord && !params.groupBy.length && params.context.product_catalog_order_model == 'stock.picking') {


                    const orderLinesInfo = await self.rpc("/product/catalog/order_lines_info", {
                        order_id: params.context["picking_id "],
                        product_ids: self.root.records.map((rec) => rec.resId),
                        res_model: params.context.product_catalog_order_model,
                    });
                    console.log("=eeeeeeeeeeeeee=e=e=e=e=e=e=e=e=e=e=e=e=", self.root.records);
                    for (const record of self.root.records) {
                            console.log("==========barcode========", record.data);
                        if (self.check) {
                            self.removeFacet(self.env.searchModel.facets[self.env.searchModel.facets.length - 1]);

                              self.env.searchModel.trigger("focus-search");
                            record.productCatalogData = orderLinesInfo[record.resId];
                            record.productCatalogData.quantity = record.productCatalogData.quantity + 1
                            self.check = false;

                            self.rpc("/product/catalog/update_order_line_info", {
                                order_id: params.context["picking_id "],
                                product_id: record.resId,
                                quantity: record.productCatalogData.quantity,
                                res_model: params.context.product_catalog_order_model,
                                barcode_cutom : self.barcode_cutom
                            });

//                            for (const update_record of self.root.records) {
//                                if (update_record.resId === record.resId) {
//                                    Object.assign(update_record, record);
//                                }
//                            }

//                            self.object_list = self.root.records;


                        }
                        else {
                            if (self.object_list.length == 0) {
                                record.productCatalogData = orderLinesInfo[record.resId];
                                self.check = false
                            }
                            else {

                                if (record.resId == self.object_list[0].resId) {
                                    record.productCatalogData = self.object_list[0].productCatalogData;
                                    self.object_list = [];
                                    self.check = false
                                }
                                else {
                                    record.productCatalogData = orderLinesInfo[record.resId];
                                    self.check = false
                                }
                            }
                        }
                        self.check = false
                    }
                  }
                  else {
                      if (!params.isMonoRecord && !params.groupBy.length){

                    const orderLinesInfo = await this.rpc("/product/catalog/order_lines_info", {
                        order_id: params.context.order_id,
                        product_ids: self.root.records.map((rec) => rec.resId),
                        res_model: params.context.product_catalog_order_model,
                        barcode_cutom : self.barcode_cutom
                    });

                    for (const record of self.root.records) {

                        if (self.check) {

                            self.removeFacet(self.env.searchModel.facets[self.env.searchModel.facets.length - 1]);
                            record.productCatalogData = orderLinesInfo[record.resId];
                            record.productCatalogData.quantity = record.productCatalogData.quantity + 1
                            self.check = false

                            self.rpc("/product/catalog/update_order_line_info", {
                                order_id: params.context.order_id,
                                product_id: record.resId,
                                quantity: record.productCatalogData.quantity,
                                res_model: params.context.product_catalog_order_model,
                                barcode_cutom : self.barcode_cutom
                            });

//                            for (const update_record of self.root.records) {
//                                if (update_record.resId === record.resId) {
//                                    Object.assign(update_record, record);
//                                }
//                            }
//
//                            self.object_list = self.root.records;

                        }
                        else {
                            if (self.object_list.length == 0) {
                                record.productCatalogData = orderLinesInfo[record.resId];
                                self.check = false
                            }
                            else {

                                if (record.resId == self.object_list[0].resId) {
                                    record.productCatalogData = self.object_list[0].productCatalogData;
                                    self.object_list = [];
                                    self.check = false
                                }
                                else {
                                    record.productCatalogData = orderLinesInfo[record.resId];
                                    self.check = false
                                }
                            }
                        }
                        self.check = false
                    }
                 }
                  }



              }


        }

        return result
    }
    removeFacet(facet) {
        var self = this
        // if (facet?.groupId != undefined) {
        self.env.searchModel.deactivateGroup(1);
        // }
    }
}

ProductCatalogKanbanModel.Record = ProductCatalogRecord;
