odoo.define("sh_pos_advance_cache.cache_product", function (require) {
    "use strict";

    var indexedDB = require('sh_pos_advance_cache.indexedDB');
    const { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const rpc = require("web.rpc");

    var indexedDB_delete = window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB || window.shimIndexedDB;
    if (!indexedDB_delete) {
        window.alert("Your browser doesn't support a stable version of IndexedDB.")
    }

    const shPosProductModel = (PosGlobalState) => class shPosProductModel extends PosGlobalState {
        send_current_order_to_customer_facing_display() {
            var self = this;
            if (this.config && !this.config.iface_customer_facing_display) return;
            if (this.config && this.config.iface_customer_facing_display) {
                this.render_html_for_customer_facing_display().then((rendered_html) => {
                    if (self.env.pos.customer_display) {
                        var $renderedHtml = $('<div>').html(rendered_html);
                        $(self.env.pos.customer_display.document.body).html($renderedHtml.find('.pos-customer_facing_display'));
                        var orderlines = $(self.env.pos.customer_display.document.body).find('.pos_orderlines_list');
                        orderlines.scrollTop(orderlines.prop("scrollHeight"));
                    } else if (this.config.iface_customer_facing_display_via_proxy && this.env.proxy.posbox_supports_display) {
                        this.env.proxy.update_customer_facing_display(rendered_html);
                    }
                });
            }
        }

       
    }
    Registries.Model.extend(PosGlobalState, shPosProductModel);

});
