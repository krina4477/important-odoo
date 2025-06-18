/** @odoo-module */

import { rpc } from "@web/core/network/rpc";
import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.get_sale_sequence_number()
    },

    async get_sale_sequence_number(){
       const seq = await rpc('/new_seq',{
                kwargs: {'old_name':this.currentOrder.pos_reference},
    }).then((res) => {
                this.currentOrder.pos_reference = res
         })
   }
})
