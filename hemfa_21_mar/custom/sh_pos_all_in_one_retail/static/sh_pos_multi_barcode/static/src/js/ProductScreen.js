odoo.define("sh_pos_multi_barcode.ProductScreen", function (require) {
    "use strict";
    
    const { Gui } = require("point_of_sale.Gui");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const Registries = require("point_of_sale.Registries");
    const ProductItem = require("point_of_sale.ProductItem");
    var field_utils = require('web.field_utils');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;


    const ShProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _getProductByBarcode(code) {
                var res = await super._getProductByBarcode(code);
                let product = this.env.pos.db.get_product_by_barcode(code.code);


                 if (product && product.barcode_line_ids && product.barcode_line_ids.length >= 1){
                     for (let i = 0; i < product.barcode_line_ids.length; i++) {
                        var dynamic_barcode =  product.barcode_line_ids[i];
                        if(code.code === this.env.pos.db.multi_barcode_by_id[dynamic_barcode].name){
                            this.env.pos.get_order().negative_qty_price = this.env.pos.db.multi_barcode_by_id[dynamic_barcode].negative_qty_price
//                            this.env.pos.get_order().allow_negative_sale_price = this.env.pos.db.multi_barcode_by_id[dynamic_barcode].allow_negative_sale_price

//                           if (!(this.env.pos.db.multi_barcode_by_id[dynamic_barcode].negative_qty_price) && !(this.env.pos.db.multi_barcode_by_id[dynamic_barcode].product_type === 'service') && res.qty_available == 0){
//                           const { confirmed } = await this.showPopup('ErrorPopup', {
//                                title: 'Quantity Not Available',
//                                body: 'You cannot add this product with '+res.qty_available+' Quantity.',
//                           });
//                           return false;
//                            }
//                             if (!(this.env.pos.db.multi_barcode_by_id[dynamic_barcode].allow_negative_sale_price) && this.env.pos.db.multi_barcode_by_id[product.barcode_line_ids[0]].price == 0){
//                                   const { confirmed } = await this.showPopup('ErrorPopup', {
//                                        title: 'Price Not Available',
//                                        body: 'You cannot add this product with '+this.env.pos.db.multi_barcode_by_id[dynamic_barcode].price+' Price.',
//                                   });
//                                   return false;
//                            }
                   }
                    }


                 }
                if(res){
                    debugger;
                    if(this.env.pos.config.sh_enable_multi_barcode){
                        if(this.env.pos.db.barcode_by_name && this.env.pos.db.barcode_by_name[code.base_code]){
                            res['negative_qty_price'] = this.env.pos.db.barcode_by_name[code.base_code].negative_qty_price
//                            res['allow_negative_sale_price'] = this.env.pos.db.barcode_by_name[code.base_code].allow_negative_sale_price
                            res['product_type'] = this.env.pos.db.barcode_by_name[code.base_code].product_type
                            res['price_lst'] = this.env.pos.db.barcode_by_name[code.base_code].price_lst
                            res['sh_barcode_price'] = this.env.pos.db.barcode_by_name[code.base_code].price
                            res['sh_barcode_uom'] = this.env.pos.db.barcode_by_name[code.base_code].unit
                        }
                        res['is_add_using_barcode'] = true
                    }
                }
                return res
            }
                    async _openProductConfiguratorPopup(product) {
    // Validate input data
    if (!Array.isArray(product.attribute_line_ids) || !this.env.pos.attributes_by_ptal_id) {
        console.error("Missing data for product.attribute_line_ids or attributes_by_ptal_id");
        console.log("product.attribute_line_ids:", product.attribute_line_ids);
        console.log("this.env.pos.attributes_by_ptal_id:", this.env.pos.attributes_by_ptal_id);
        return { confirmed: false }; // Exit early if data is missing
    }

    // Map and filter attributes
    let attributes = product.attribute_line_ids
        .map((id) => this.env.pos.attributes_by_ptal_id[id])
        .filter((attr) => attr && Array.isArray(attr.values));

    // Avoid opening the popup if each attribute has only one option
    const hasMultipleOptions = attributes.some((attribute) =>
        attribute.values.length > 1 || attribute.values.some((value) => value.is_custom)
    );

    if (hasMultipleOptions) {
        return await this.showPopup('ProductConfiguratorPopup', {
            product: product,
            attributes: attributes,
        });
    }

    // Auto-select attributes if no popup is needed
    let selected_attributes = [];
    let price_extra = 0.0;

    attributes.forEach((attribute) => {
        if (attribute.values && attribute.values.length > 0) {
            const firstValue = attribute.values[0];
            selected_attributes.push(firstValue.name || "Unnamed Attribute");
            price_extra += firstValue.price_extra || 0.0;
        }
    });

    return {
        confirmed: true,
        payload: {
            selected_attributes,
            price_extra,
        },
    };
}

        async _getAddProductOptions(product, code) {
            let price_extra = 0.0;
            let draftPackLotLines, weight, description, packLotLinesToEdit;
            if (_.some(product.attribute_line_ids, (id) => id in this.env.pos.attributes_by_ptal_id)) {
                let { confirmed, payload } = await this._openProductConfiguratorPopup(product);
                if (confirmed) {
                    description = payload.selected_attributes.join(', ');
                    price_extra += payload.price_extra;
                } else {
                    return;
                }
            }
            console.log("=ccc=cc==c=cc==c=c=c=cc=c=c=c=c=c=c=c=c=c=c=c=c=c=1111");
            // Gather lot information if required.
            if (['serial', 'lot'].includes(product.tracking) && (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots)) {
                const isAllowOnlyOneLot = product.isAllowOnlyOneLot();
                if (isAllowOnlyOneLot) {
                    packLotLinesToEdit = [];
                } else {
                    const orderline = this.currentOrder
                        .get_orderlines()
                        .filter(line => !line.get_discount())
                        .find(line => line.product.id === product.id);
                    if (orderline) {
                        packLotLinesToEdit = orderline.getPackLotLinesToEdit();
                    } else {
                        packLotLinesToEdit = [];
                    }
                }
                // if the lot information exists in the barcode, we don't need to ask it from the user.
                if (code && code.type === 'lot') {
                    // consider the old and new packlot lines
                    const modifiedPackLotLines = Object.fromEntries(
                        packLotLinesToEdit.filter(item => item.id).map(item => [item.id, item.text])
                    );
                    const newPackLotLines = [
                        { lot_name: code.code },
                    ];
                    draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
                } else {
                    const { confirmed, payload } = await this.showPopup('EditListPopup', {
                        title: this.env._t('Lot/Serial Number(s) Required'),
                        isSingleItem: isAllowOnlyOneLot,
                        array: packLotLinesToEdit,
                    });
                    if (confirmed) {
                        // Segregate the old and new packlot lines
                        const modifiedPackLotLines = Object.fromEntries(
                            payload.newArray.filter(item => item.id).map(item => [item.id, item.text])
                        );
                        const newPackLotLines = payload.newArray
                            .filter(item => !item.id)
                            .map(item => ({ lot_name: item.text }));

                        draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
                    } else {
                        // We don't proceed on adding product.
                        return;
                    }
                }
            }

            // Take the weight if necessary.
            if (product.to_weight && this.env.pos.config.iface_electronic_scale) {
                // Show the ScaleScreen to weigh the product.
                if (this.isScaleAvailable) {
                    const { confirmed, payload } = await this.showTempScreen('ScaleScreen', {
                        product,
                    });
                    if (confirmed) {
                        weight = payload.weight;
                    } else {
                        // do not add the product;
                        return;
                    }
                } else {
                    await this._onScaleNotAvailable();
                }
            }
            if (code && this.env.pos.db.product_packaging_by_barcode[code.code]) {
                weight = this.env.pos.db.product_packaging_by_barcode[code.code].qty;
            }

            return { draftPackLotLines, quantity: weight, description, price_extra };
        }

            async _barcodeProductAction(code) {
                debugger;
                var self = this;
                let product = this.env.pos.db.get_product_by_barcode(code.code);
                var order = this.env.pos.get_order()
                var products = this.env.pos.db.get_product_by_barcode(code.code)
                var rpc = require('web.rpc');
                if (product && product.barcode_line_ids && product.barcode_line_ids.length >= 1){

                 for (let i = 0; i < product.barcode_line_ids.length; i++) {
                        var dynamic_barcode =  product.barcode_line_ids[i];
                        if(code.code === this.env.pos.db.multi_barcode_by_id[dynamic_barcode].name){
//
                              this.env.pos.get_order().negative_qty_price = this.env.pos.db.multi_barcode_by_id[dynamic_barcode].negative_qty_price
//                              this.env.pos.get_order().allow_negative_sale_price = this.env.pos.db.multi_barcode_by_id[dynamic_barcode].allow_negative_sale_price

                              var stock_quants = await this.rpc({
                                model: "stock.quant",
                                method: 'search_read',
                                domain: [['product_id','=',products.id],['on_hand', '=', true]],
                                })

                                var product_uom = this.env.pos.units_by_id[this.env.pos.db.multi_barcode_by_id[dynamic_barcode].unit[0]]

                                if (! (this.env.pos.db.multi_barcode_by_id[dynamic_barcode].negative_qty_price) && !(this.env.pos.db.multi_barcode_by_id[dynamic_barcode].product_type === 'service')){
                                    console.log("ssssssssssssssssss");
//                                    var res = order.get_total_orders(products,product_uom,self,stock_quants)
//
//                                    if (!(res)){
//                                        return res
//                                    }

                                }
                   }
                    }



                }
                if (product && product.active === false){
                    return;
                }
                if(self.env.pos.get_order().get_orderlines().find(line => line.same_barcode_product == code.code)){
                                let product_qty =self.env.pos.get_order().get_orderlines().find(line => line.same_barcode_product == code.code);
                                product_qty.set_quantity(product_qty.quantity+1)
                }else if(self.env.pos.get_order().get_orderlines().find(line => line.barcode_code == code.code)){
                                let product_qty =self.env.pos.get_order().get_orderlines().find(line =>line.barcode_code == code.code);
                                product_qty.set_quantity(product_qty.quantity+1)
                }
                else
                {


                await super._barcodeProductAction(code);
                if(this.env.pos.get_order().get_selected_orderline() && this.env.pos.db.barcode_by_name[code.base_code]){
                    this.env.pos.get_order().get_selected_orderline().barcode_code = code.base_code;
                    this.env.pos.get_order().get_selected_orderline().barcode_orderline = code.code;
                }
                if(this.env.pos.get_order().get_selected_orderline() && this.env.pos.get_order().get_selected_orderline().get_product().is_add_using_barcode && this.env.pos.get_order().get_selected_orderline().get_product().sh_barcode_price && this.env.pos.get_order().get_selected_orderline().get_product().price_lst){
                    this.env.pos.get_order().get_selected_orderline().set_unit_price(this.env.pos.get_order().get_selected_orderline().get_product().sh_barcode_price)
                    this.env.pos.get_order().get_selected_orderline().price = this.env.pos.get_order().get_selected_orderline().get_product().sh_barcode_price
                    this.env.pos.get_order().get_selected_orderline().price_manually_set = true
                }
    //                if(this.env.pos.get_order().get_selected_orderline() && this.env.pos.get_order().get_selected_orderline().get_product().is_add_using_barcode && this.env.pos.get_order().get_selected_orderline().get_product().sh_barcode_price && !this.env.pos.get_order().get_selected_orderline().get_product().price_lst){
    ////                    this.env.pos.get_order().get_selected_orderline().set_unit_price(this.env.pos.get_order().get_selected_orderline().get_product().sh_barcode_price)
    //                    this.env.pos.get_order().get_selected_orderline().price = this.env.pos.get_order().get_selected_orderline().get_product().sh_barcode_price
    //                    this.env.pos.get_order().get_selected_orderline().price_manually_set = true
    //                }
                if(this.env.pos.get_order().get_selected_orderline() && this.env.pos.get_order().get_selected_orderline().get_product().is_add_using_barcode && !this.env.pos.get_order().get_selected_orderline().get_product().sh_barcode_price && this.env.pos.get_order().get_selected_orderline().get_product().price_lst){
                    var pricelist = ''
                    if(this.env.pos.get_order().get_selected_orderline().get_product().price_lst[0]){
                        pricelist = this.env.pos.db.pricelist_by_id[this.env.pos.get_order().get_selected_orderline().get_product().price_lst[0]]
                    }else{
                        pricelist = this.env.pos.db.pricelist_by_id[this.env.pos.get_order().get_selected_orderline().get_product().price_lst]
                    }

                    if(pricelist){
                        let productSearched = this.env.pos.db.barcode_by_name[code.code]

                        if (productSearched){
                            var price = 0;
                            var quantity = 1;
                            var date = moment();
                            _.find(pricelist.item_ids, function (item_id) {
                                let rule = self.env.pos.db.pricelist_item_by_id[item_id]
                                var productObj = self.env.pos.db.get_product_by_id(productSearched.product_id)

                                var sh_unit;
                                if (productSearched.unit && productSearched.unit[0]){
                                    sh_unit = productSearched.unit[0]
                                }else{
                                    sh_unit = productSearched.unit
                                }
                                if (rule) {
                                    if (((productObj.id == rule.product_id[0]) || productObj.product_tmpl_id == rule.product_tmpl_id[0]) && sh_unit == rule.uom_id[0] && (
                                        (!rule.categ_id || _.contains(self.parent_category_ids.concat(self.categ.id), rule.categ_id[0])) &&
                                        (!rule.date_start || moment.utc(rule.date_start).isSameOrBefore(date)) &&
                                        (!rule.date_end || moment.utc(rule.date_end).isSameOrAfter(date))
                                        )){
                                        if (rule.min_quantity && quantity < rule.min_quantity) {
                                            return false;
                                        }
                                        if (rule.base === 'pricelist') {
                                            let base_pricelist = _.find(self.env.pos.pricelists, function (pricelist) {
                                                return pricelist.id === rule.base_pricelist_id[0];});
                                            if (base_pricelist) {
                                                price = self.get_price(base_pricelist, quantity);
                                            }
                                        } else if (rule.base === 'standard_price') {
                                            price = self.standard_price;
                                        }

                                        if (rule.compute_price === 'fixed') {
                                            price = rule.fixed_price;
                                            return true;
                                        } else if (rule.compute_price === 'percentage') {
                                            price = price - (price * (rule.percent_price / 100));
                                            return true;
                                        } else {
                                            var price_limit = price;
                                            price = price - (price * (rule.price_discount / 100));
                                            if (rule.price_round) {
                                                price = round_pr(price, rule.price_round);
                                            }
                                            if (rule.price_surcharge) {
                                                price += rule.price_surcharge;
                                            }
                                            if (rule.price_min_margin) {
                                                price = Math.max(price, price_limit + rule.price_min_margin);
                                            }
                                            if (rule.price_max_margin) {
                                                price = Math.min(price, price_limit + rule.price_max_margin);
                                            }
                                        }
                                    }
                                }
                            })

                            var secondaryUom;
                            if (productSearched.unit && productSearched.unit[0]){
                                secondaryUom = this.env.pos.units_by_id[productSearched.unit[0]]
                            } else{
                                secondaryUom = this.env.pos.units_by_id[productSearched.unit]
                            }

                            if (secondaryUom){
                                let converted_price  = price / secondaryUom.ratio
                                if (converted_price){
                                    this.env.pos.get_order().get_selected_orderline().price_manually_set = true
                                    this.env.pos.get_order().get_selected_orderline().is_price_convert = true

                                    this.env.pos.get_order().get_selected_orderline().set_unit_price(converted_price)
                                }else{
//                                    if (this.env.pos.get_order() && this.env.pos.get_order().get_selected_orderline()){
//                                        this.env.pos.get_order().remove_orderline(this.env.pos.get_order().get_selected_orderline())
//                                    }
//                                    await self.showPopup("ErrorPopup", {
//                                        title: 'Barcode !',
//                                        body: 'Rule Not Found',
//                                    })
                                }
                            }
                        } else {
                        // this.env.pos.get_order().get_selected_orderline().set_unit_price(this.env.pos.get_order().get_selected_orderline().product.get_price(pricelist, this.env.pos.get_order().get_selected_orderline().get_quantity(), this.env.pos.get_order().get_selected_orderline().get_price_extra()));
                        }
                    }
                }
                if(this.env.pos.get_order().get_selected_orderline() && this.env.pos.get_order().get_selected_orderline().get_product().is_add_using_barcode && this.env.pos.get_order().get_selected_orderline().get_product().sh_barcode_uom){
                    var units = ''
                    if(this.env.pos.get_order().get_selected_orderline().get_product().sh_barcode_uom[0]){
                        units = this.env.pos.units_by_id[this.env.pos.get_order().get_selected_orderline().get_product().sh_barcode_uom[0]]
                    }else{
                        units = this.env.pos.units_by_id[this.env.pos.get_order().get_selected_orderline().get_product().sh_barcode_uom]
                    }

                    if(units){
                        var rr = this.env.pos.get_order().get_selected_orderline().change_current_uom(units);
                        // this.env.pos.get_order().get_selected_orderline().set_quantity(1);

                    }
                }

                if(this.env.pos.get_order() && this.env.pos.get_order().get_selected_orderline()){
                    this.env.pos.get_order().get_selected_orderline()['negative_qty_price'] = this.env.pos.get_order().get_selected_orderline().get_product()['negative_qty_price']
//                    this.env.pos.get_order().get_selected_orderline()['allow_negative_sale_price'] = this.env.pos.get_order().get_selected_orderline().get_product()['allow_negative_sale_price']
                    this.env.pos.get_order().get_selected_orderline().get_product()['negative_qty_price'] = ''

                }
            }




                }

        };
    Registries.Component.extend(ProductScreen, ShProductScreen);

    const shMultiBarcodeProductItem = (ProductItem) =>
        class extends ProductItem {
            get price() {
                var self = this
                var price_val =  super.price
                if(this.env.pos.config.sh_enable_multi_barcode && this.env.pos.product_search){
                    if(this.env.pos.db.barcode_by_name[this.env.pos.product_search]){
                        if(this.env.pos.db.barcode_by_name[this.env.pos.product_search].price){
                            return this.env.pos.db.barcode_by_name[this.env.pos.product_search].price
                        }else if(this.env.pos.db.barcode_by_name[this.env.pos.product_search].price_lst){
                            let product = this.env.pos.db.barcode_by_name[this.env.pos.product_search]
                            var pricelist = this.env.pos.db.pricelist_by_id[this.env.pos.db.barcode_by_name[this.env.pos.product_search].price_lst]
                            if(pricelist){
                                // var price = this.props.product.get_price(pricelist, 1, 0)
                                var price = 0;
                                var quantity = 1;
                                var date = moment();
                                _.find(pricelist.item_ids, function (item_id) {
                                    let rule = self.env.pos.db.pricelist_item_by_id[item_id]

                                    var productObj = self.env.pos.db.get_product_by_id(product.product_id)

                                    if (((productObj.id == rule.product_id) || productObj.product_tmpl_id == rule.product_tmpl_id[0]) && product.unit == rule.uom_id[0] && (
                                        (!rule.categ_id || _.contains(self.parent_category_ids.concat(self.categ.id), rule.categ_id[0])) &&
                                        (!rule.date_start || moment.utc(rule.date_start).isSameOrBefore(date)) &&
                                        (!rule.date_end || moment.utc(rule.date_end).isSameOrAfter(date))
                                    )){
                                        if (rule.min_quantity && quantity < rule.min_quantity) {
                                            return false;
                                        }
                                        if (rule.base === 'pricelist') {
                                            let base_pricelist = _.find(self.pos.pricelists, function (pricelist) {
                                                return pricelist.id === rule.base_pricelist_id[0];});
                                            if (base_pricelist) {
                                                price = self.get_price(base_pricelist, quantity);
                                            }
                                        } else if (rule.base === 'standard_price') {
                                            price = self.standard_price;
                                        }

                                        if (rule.compute_price === 'fixed') {
                                            price = rule.fixed_price;
                                            return true;
                                        } else if (rule.compute_price === 'percentage') {
                                            price = price - (price * (rule.percent_price / 100));
                                            return true;
                                        } else {
                                            var price_limit = price;
                                            price = price - (price * (rule.price_discount / 100));
                                            if (rule.price_round) {
                                                price = round_pr(price, rule.price_round);
                                            }
                                            if (rule.price_surcharge) {
                                                price += rule.price_surcharge;
                                            }
                                            if (rule.price_min_margin) {
                                                price = Math.max(price, price_limit + rule.price_min_margin);
                                            }
                                            if (rule.price_max_margin) {
                                                price = Math.min(price, price_limit + rule.price_max_margin);
                                            }
                                        }
                                    }
                                })
                                return price
                            }
                        }
                    }
                }
                return price_val
            }
        }

    Registries.Component.extend(ProductItem, shMultiBarcodeProductItem)
});