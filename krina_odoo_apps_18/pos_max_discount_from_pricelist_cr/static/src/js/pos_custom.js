/** @odoo-module */

import { patch } from "@web/core/utils/patch";
const { DateTime } = luxon;
import { registry } from "@web/core/registry";
import { formatCurrency } from "@point_of_sale/app/models/utils/currency";
import { ProductProduct } from "@point_of_sale/app/models/product_product";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

Orderline.props.line.shape = {
    ...Orderline.props.line.shape,
    pricelist_label: String,
    pricelist_discount_label: String,
};

patch(PosOrderline.prototype, {
    setup() {
        super.setup(...arguments);
        this.pricelist_id = this.pricelist_id || false;
        this.pricelist_label = this.pricelist_label || false;
        this.pricelist_discount_label = this.pricelist_discount_label || false;
    },

    //@override
    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        this.pricelist_id  = json.pricelist_id;
        this.pricelist_label = json.pricelist_label;
        this.pricelist_discount_label = json.pricelist_discount_label;
    },

    //@override
    export_as_JSON(){
        const json = super.export_as_JSON(...arguments);
        if(json){
            json.pricelist_id  = this.pricelist_id;
            json.pricelist_label = this.pricelist_label;
            json.pricelist_discount_label = this.pricelist_discount_label;
            return json;
        }
     },

    getDisplayData() {
        return {
            productName: this.get_full_product_name(),
            price: this.getPriceString(),
            qty: this.get_quantity_str(),
            unit: this.product_id.uom_id ? this.product_id.uom_id.name : "",
            unitPrice: formatCurrency(this.get_unit_display_price(), this.currency),
            oldUnitPrice: this.get_old_unit_display_price()
                ? formatCurrency(this.get_old_unit_display_price(), this.currency)
                : "",
            discount: this.get_discount_str(),
            customerNote: this.get_customer_note() || "",
            internalNote: this.getNote(),
            comboParent: this.combo_parent_id?.get_full_product_name?.() || "",
            packLotLines: this.pack_lot_ids.map(
                (l) =>
                    `${l.pos_order_line_id.product_id.tracking == "lot" ? "Lot Number" : "SN"} ${
                        l.lot_name
                    }`
            ),
            price_without_discount: formatCurrency(
                this.getUnitDisplayPriceBeforeDiscount(),
                this.currency
            ),
            taxGroupLabels: [
                ...new Set(
                    this.product_id.taxes_id
                        ?.map((tax) => tax.tax_group_id.pos_receipt_label)
                        .filter((label) => label)
                ),
            ].join(" "),
            pricelist_label: this.pricelist_label || "",
            pricelist_discount_label:this.pricelist_discount_label || "",
        };
    },

     get_pricelist_label(){
        return this.pricelist_label;
     },

     set_pricelist_label(name){
        this.pricelist_label = name;
     },

     get_pricelist_id(){
        return this.pricelist_id;
     },

     set_pricelist_id(id){
        this.pricelist_id = id;
     },

     get_pricelist_discount_label(){
         return this.pricelist_discount_label;
     },

     set_pricelist_discount_label(name){
        this.pricelist_discount_label = name;
     }
});

patch(PosOrder.prototype, {
    setup() {
        super.setup(...arguments);
    },

    select_orderline(line) {
        super.select_orderline(...arguments);
        this.get_pricelist_label(line);
    },

    get_pricelist_label(lines){
        var line = lines;
            if (line){
                var quantity = line.qty;
                var price_extra = line.price_extra;

                var self = this;
                var date = DateTime.now().startOf("day");
                var price = line.product_id.lst_price;
                var product_id = line.product_id.id

                var default_price = line.product_id.lst_price;
                if (price_extra){
                    default_price += price_extra;
                }

                if (posmodel.config.use_pricelist){
                    var pricelist_price_dict = {}
                    var element=Array.from(posmodel.config.available_pricelist_ids)
                    element.forEach((pricelists) =>{

                        var items=pricelists.item_ids
                        var pricelist_items = items.filter((item) => {
                            return (item._raw.product_tmpl_id === self.get_selected_orderline().product_id.raw.product_tmpl_id) &&
                                   (item._raw.product_id ? item._raw.product_id === self.get_selected_orderline().product_id.raw.id : true) &&
                                   (item._raw.categ_id ? category_ids.contains(item._raw.categ_id[0]) : true) &&
                                   (item._raw.date_start ? moment(item._raw.date_start).isSameOrBefore(date) : true) &&
                                   (item._raw.date_end ? moment(item._raw.date_end).isSameOrAfter(date) : true);
                        });
                        var pricelist_rule_items = {}

                        pricelist_items.find((rule) => {
                            var temp_price = default_price

                            if (rule.min_quantity && quantity < rule.min_quantity) {
                                pricelist_rule_items[rule.id] = temp_price
                                return false;
                            }
                            if (rule.base === 'pricelist') {
                                temp_price = self.get_price(rule.base_pricelist, quantity);
                                pricelist_rule_items[rule.id] = temp_price
                            } else if (rule.base === 'standard_price') {
                                temp_price = self.standard_price;
                                pricelist_rule_items[rule.id] = temp_price
                            }


                            if (rule.compute_price === 'fixed')
                            {
                                temp_price = rule.fixed_price;
                                pricelist_rule_items[rule.id] = temp_price
                                return true;
                            }
                            else if (rule.compute_price === 'percentage')
                            {
                                temp_price = temp_price - (temp_price * (rule.percent_price / 100));
                                pricelist_rule_items[rule.id] = temp_price
                                return true;
                            }
                            else
                            {
                                var price_limit = price;
                                temp_price = temp_price - (temp_price * (rule.price_discount / 100));

                                if (rule.price_round) {
                                    temp_price = round_pr(temp_price, rule.price_round);
                                }
                                if (rule.price_surcharge) {
                                    temp_price += rule.price_surcharge;
                                }

                                if (rule.price_min_margin) {
                                    temp_price = Math.max(temp_price, price_limit + rule.price_min_margin);
                                }
                                if (rule.price_max_margin) {
                                    temp_price = Math.min(temp_price, price_limit + rule.price_max_margin);
                                }

                                pricelist_rule_items[rule.id] = temp_price
                                return true;
                            }
                            pricelist_rule_items[rule.id] = temp_price
                            return false;
                       })
                        var minKey = Object.keys(pricelist_rule_items)[0]
                        pricelist_price_dict[pricelists.id] = pricelist_rule_items[minKey]

                    });
                    Object.keys(pricelist_price_dict).forEach((maxpricelist) =>{
                        var minpriceKey = maxpricelist
                        if(price == pricelist_price_dict[minpriceKey]  ) {
                            line.set_pricelist_discount_label(false);
                            line.set_pricelist_label(false);
                            line.set_pricelist_id(false);

                        }
                        else if(price < pricelist_price_dict[minpriceKey] || price > pricelist_price_dict[minpriceKey] ){

                        var name = false;
                        var policy = false;
                        posmodel.config.available_pricelist_ids.forEach((pricelists)=> {
                            if (pricelists.id === parseInt(minpriceKey)  ){

                                name = pricelists.name
                                policy = pricelists.discount_policy
                            }

                        });

                        line.set_pricelist_discount_label(policy);
                        line.set_pricelist_label(name);
                        line.set_pricelist_id(minpriceKey);

                    }
                    })
                }
            }
         return true
    }
});

patch(ProductProduct.prototype,{
    setup(){
        super.setup(...arguments);
    },

    get_price(pricelist, quantity, price_extra = 0, recurring = false) {
        var self = this;
        var date = DateTime.now().startOf("day");
        var price = super.get_price(...arguments);
        var default_price = self.lst_price;
        if (price_extra){
            default_price += price_extra;
        }
        if (posmodel.config.use_pricelist){
            var pricelist_price_dict = {}
            posmodel.config.available_pricelist_ids.forEach(function (pricelists) {
                var pricelist_items = pricelists.item_ids.filter(function (item) {
                    return (item._raw.product_tmpl_id === self._raw.product_tmpl_id) &&
                        (item._raw.product_id ? item._raw.product_id === self.id : true) &&
                        (item._raw.categ_id ? category_ids.contains(item._raw.categ_id[0]) : true) &&
                        (item._raw.date_start ? moment(item._raw.date_start).isSameOrBefore(date) : true) &&
                        (item._raw.date_end ? moment(item._raw.date_end).isSameOrAfter(date) : true);
                });
                var pricelist_rule_items = {}

                pricelist_items.find(function (rule) {
                    var temp_price = default_price
                    if (rule.min_quantity && quantity < rule.min_quantity) {
                        pricelist_rule_items[rule.id] = temp_price
                        return false;
                    }

                    if (rule.base === 'pricelist') {
                        temp_price = self.get_price(rule.base_pricelist, quantity);
                        pricelist_rule_items[rule.id] = temp_price
                    } else if (rule.base === 'standard_price') {

                        temp_price = self.standard_price;
                        pricelist_rule_items[rule.id] = temp_price
                    }

                    if (rule.compute_price === 'fixed') {
                        temp_price = rule.fixed_price;
                        pricelist_rule_items[rule.id] = temp_price
                        return true;
                    } else if (rule.compute_price === 'percentage') {
                        temp_price = temp_price - (temp_price * (rule.percent_price / 100));
                        pricelist_rule_items[rule.id] = temp_price
                        return true;
                    } else {
                        var price_limit = price;
                        temp_price = temp_price - (temp_price * (rule.price_discount / 100));
                        if (rule.price_round) {
                            temp_price = round_pr(temp_price, rule.price_round);
                        }
                        if (rule.price_surcharge) {
                            temp_price += rule.price_surcharge;
                        }
                        if (rule.price_min_margin) {
                            temp_price = Math.max(temp_price, price_limit + rule.price_min_margin);
                        }
                        if (rule.price_max_margin) {
                            temp_price = Math.min(temp_price, price_limit + rule.price_max_margin);
                        }
                        pricelist_rule_items[rule.id] = temp_price
                        return true;
                    }
                    pricelist_rule_items[rule.id] = temp_price
                    return false;
                });

                var minKey = Object.keys(pricelist_rule_items)
                pricelist_price_dict[pricelists.id] = pricelist_rule_items[minKey]
                var minpriceKey = Object.keys(pricelist_price_dict)[minKey]
	    		if(price > pricelist_price_dict[minKey]) {
	    			price = pricelist_price_dict[minKey]
	    		}
            });
	    		posmodel.get_order().get_pricelist_label(posmodel.get_order().get_selected_orderline())
	    	}
        return price;
	}
})








