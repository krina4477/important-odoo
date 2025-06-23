
/* @odoo-module */
const ProductScreen = require('point_of_sale.ProductScreen');
const Registries = require('point_of_sale.Registries');
const { Gui } = require('point_of_sale.Gui');

export const PosZeroQuantityRestrictProductScreen = (ProductScreen) =>
  class extends ProductScreen {
    //@override
    async _onClickPay() {
      const orderLines = this.env.pos.get_order().orderlines;
      if (orderLines.length === 0) {
              // Do not confirm the order and show error popup
              Gui.showPopup('ErrorPopup', {
                title: 'Empty Order Line',
                body: 'Cashier Can Not Validate This Order Because The Order Is Empty',
              });
              return;
      }
      for (let i = 0; i < orderLines.length; i++) {
        const qty = orderLines[i].quantity;
        if (orderLines[i].negative_qty_price != true && !(orderLines[i].product_type == 'service')){

              var stock_quants = await this.rpc({
                 model: "stock.quant",
                 method: 'search_read',
                 domain: [['product_id','=', orderLines[i].product.id]],
             })
             var picking_type =  this.env.pos.db.picking_type_by_id[this.env.pos.config.picking_type_id[0]].default_location_src_id[0];
             for (let m=0;m<stock_quants.length;m++){
                    if (picking_type === stock_quants[m].location_id[0]){
                       var stock_quant_info = stock_quants[m]
                    }
             }

            if (qty === 0) {
              // Do not confirm the order and show error popup
              Gui.showPopup('ErrorPopup', {
                title: 'Zero quantity not allowed',
                body: 'Only a positive quantity is allowed for confirming the order',
              });
              return;
            }
            if (qty > stock_quant_info.quantity) {
              Gui.showPopup('ErrorPopup', {
                 title: 'Cannot Add Product',
                 body: 'You cannot add this product '+ orderLines[i].product.display_name + '  with only '+ stock_quant_info.quantity + ' available.',
              });
              return; // Exit the loop and do not proceed with confirming the order
            }

        }
        if (orderLines[i].allow_negative_sale_price != true){
            if (orderLines[i].price === 0) {
              // Do not confirm the order and show error popup
              Gui.showPopup('ErrorPopup', {
                 title: 'Price Not Available',
                 body: '  You cannot add this product '+ orderLines[i].product.display_name + ' with only '+ orderLines[i].price + ' Price.',
              });
              return; // Exit the loop and do not proceed with confirming the order
            }

        }
      }
      await super._onClickPay(...arguments);
    }
  };

Registries.Component.extend(ProductScreen, PosZeroQuantityRestrictProductScreen);