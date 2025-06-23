odoo.define("sh_pos_secondary.SelectionPopup", function (require) {
    "use strict";

    const SelectionPopup = require("point_of_sale.SelectionPopup");
    const Registries = require('point_of_sale.Registries');

    const ShSelectionPopup = (SelectionPopup) =>
        class extends SelectionPopup {
            setup(){
                super.setup()
            }

           selectItem(itemId)  {
               var self = this
               if(this.props.title == "Select the UOM") {
                 $(self.props.list).each(async function(index, product_list){
                        var this_product = this
                        var uom_product_set = Number(this.item.product_id && this.item.product_id[0])
                        if (!uom_product_set){
                            uom_product_set = Number(this.item.product_id)

                        }

                        console.log("index",index)
                        var uom = this.unit
                        var add_dynamic_barcode_item = this_product.item
                        var rpc = require("web.rpc");
                        if(itemId == this_product.id) {

                         self.env.pos.get_order().product_type = add_dynamic_barcode_item.product_type;
                         if (this_product['item']['product_id'][0]) {
                             if (!(this.item.negative_qty_price) && !(this.item.product_type === 'service') && self.env.pos.db.product_by_id[this_product['item']['product_id'][0]].qty_available === 0) {

//                                 self.showPopup('ErrorPopup', {
//                                    title: 'Cannot Add Product',
//                                    body: 'You cannot add this product with '+self.env.pos.db.product_by_id[this_product['item']['product_id'][0]].qty_available+' quantity available.',
//                                });
//                                return;
                             }

                         }else {
                            if (!(this.item.negative_qty_price) && !(this.item.product_type === 'service') && self.env.pos.db.product_by_id[this_product.item.product_id].qty_available === 0) {
//                                 self.showPopup('ErrorPopup', {
//                                    title: 'Cannot Add Product',
//                                    body: 'You cannot add this product with '+self.env.pos.db.product_by_id[this_product.item.product_id].qty_available+' quantity available.',
//                                });
//                                return;
                            }
                         }

//                         if (!(this.item.allow_negative_sale_price) && this.item.price === 0) {
//                                 self.showPopup('ErrorPopup', {
//                                    title: 'Cannot Add Product',
//                                    body: 'You cannot add this product with '+this.item.price+' price.',
//                                });
//                                return;
//                         }
                            if(self.env.pos.get_order().get_orderlines().find(line => line.same_barcode_product ===  this_product.label)  ){
                                    let update_line = self.env.pos.get_order().get_orderlines().find(line => line.same_barcode_product === this_product.label);
                                    var order = self.env.pos.get_order()
                                    // Check if this_product.item.product_id[0] then assign in product object
                                    if (this_product.item.product_id[0]){
                                        var product = self.env.pos.db.get_product_by_id(this_product.item.product_id[0])
                                    }
                                    else{
                                        var product = self.env.pos.db.get_product_by_id(this_product.item.product_id)
                                    }
                                    var stock_quants = await self.rpc({
                                        model: "stock.quant",
                                        method: 'search_read',
                                        domain: [['product_id','=',product.id]],
                                    })
                                    var product_uom = self.env.pos.units_by_id[this_product.item.unit[0]]
                                     if (! (this.item.negative_qty_price) ){
                                          console.log("sssssssssssssssss33333333333333333s");
//                                          var res = order.get_total_orders(product,product_uom,self,stock_quants)
//                                          if (!(res)){
//                                                return res
//                                          }
                                     }
                                    update_line.set_quantity(update_line.quantity+1)
                            }

                            else{
                            if(self.env.pos.get_order().get_selected_orderline() && self.env.pos.get_order().get_selected_orderline().same_barcode_product == this_product.label){
                                 var order = self.env.pos.get_order()
                                 if (this_product.item.product_id[0]){
                                    var product = self.env.pos.db.get_product_by_id(this_product.item.product_id[0])
                                 }
                                 else{
                                    var product = self.env.pos.db.get_product_by_id(this_product.item.product_id)
                                 }
                                 var stock_quants = await self.rpc({
                                    model: "stock.quant",
                                    method: 'search_read',
                                    domain: [['product_id','=',product.id]],
                                 })
                                 var product_uom = self.env.pos.units_by_id[this_product.item.unit[0]]
                                 if (! (this.item.negative_qty_price ) && !(this.item.product_type === 'service')){
                                      console.log("sssssssssssssssss5555555555555555s");
//                                       var res = order.get_total_orders(product,product_uom,self,stock_quants)
//                                       if (!(res)){
//                                            return res
//                                       }
                                 }
                                 self.env.pos.get_order().get_selected_orderline().set_quantity(self.env.pos.get_order().get_selected_orderline().quantity+1)

                            }
                            else if(self.env.pos.get_order().get_orderlines().find(line => line.barcode_orderline == this_product.label)  ){
                                            let update_line_barcode =self.env.pos.get_order().get_orderlines().find(line => line.barcode_orderline === this_product.label);
                                            var order = self.env.pos.get_order()
                                            if (this_product.item.product_id[0]){
                                                var product = self.env.pos.db.get_product_by_id(this_product.item.product_id[0])
                                            }
                                            else{
                                                var product = self.env.pos.db.get_product_by_id(this_product.item.product_id,this.item.negative_qty_price)
                                            }
                                            var stock_quants = await self.rpc({
                                                model: "stock.quant",
                                                method: 'search_read',
                                                domain: [['product_id','=',product.id]],
                                            })
                                            var product_uom = self.env.pos.units_by_id[this_product.item.unit[0]]
                                            if (! (this.item.negative_qty_price) && !(this.item.product_type === 'service') ){
                                               console.log("ssssssssssssssssss57777777777777777");
//                                                var res = order.get_total_orders(product,product_uom,self,stock_quants)
//                                                if (!(res)){
//                                                    return res
//                                                }
                                            }
                                            update_line_barcode.set_quantity(update_line_barcode.quantity+1)
                            }
                            else{
                                        var order = self.env.pos.get_order()
                                        if (this_product.item.product_id[0]){
                                            var product = self.env.pos.db.get_product_by_id(this_product.item.product_id[0])
                                        }
                                        else{
                                            var product = self.env.pos.db.get_product_by_id(this_product.item.product_id)
                                        }
                                        var stock_quants = await self.rpc({
                                            model: "stock.quant",
                                            method: 'search_read',
                                            domain: [['product_id','=',product.id]],
                                        })
                                        var product_uom = self.env.pos.units_by_id[this_product.item.unit[0]]
                                        if (! (this.item.negative_qty_price) && !(this.item.product_type === 'service') ){
//                                          console.log("ssssssssssssssssss67777777777777777777");
//                                           var res = order.get_total_orders(product,product_uom,self,stock_quants)
//                                           if (!(res)){
//                                                return res
//                                           }
                                        }
                                        self.env.pos.get_order().add_product(self.env.pos.db.product_by_id[uom_product_set], {
                                            price: this_product.item.price,
                                            merge: false,
                                            lst_price: this_product.item.price,
                                            extras: {
                                                price_manually_set: true,
                                            },
                                        });
                                        self.env.pos.get_order().get_selected_orderline().same_barcode_product = this_product.label
                                        var secondaryUom;
                                        if (add_dynamic_barcode_item.unit && add_dynamic_barcode_item.unit[0]){
                                            secondaryUom = self.env.pos.units_by_id[add_dynamic_barcode_item.unit[0]]
                                        }else{
                                            secondaryUom = self.env.pos.units_by_id[add_dynamic_barcode_item.unit]
                                        }
                                        self.env.pos.get_order().get_selected_orderline().change_current_uom(secondaryUom);
                                        self.env.pos.get_order().get_selected_orderline().barcode_add = this_product.label;
                                        self.env.pos.get_order().get_selected_orderline().negative_qty_price = add_dynamic_barcode_item.negative_qty_price;
                                        self.env.pos.get_order().orderlines.negative_qty_price = add_dynamic_barcode_item.negative_qty_price;
//                                        self.env.pos.get_order().get_selected_orderline().allow_negative_sale_price = add_dynamic_barcode_item.allow_negative_sale_price;
//                                        self.env.pos.get_order().orderlines.allow_negative_sale_price = add_dynamic_barcode_item.allow_negative_sale_price;
                                        self.env.pos.get_order().product_type = add_dynamic_barcode_item.product_type;

                            }


                            }

                        }


                })

               }
               else{
                self.state.selectedId = itemId;
                self.confirm();
               }
          }

          add_class(event){
                let clicked_row = Number(this.item.product_id)
                if($(clicked_row).hasClass("highlight")){
                    $(clicked_row).removeClass()
                }
                else{
                    $(clicked_row).addClass("highlight")
                }
            }
        }

    Registries.Component.extend(SelectionPopup, ShSelectionPopup)

});