odoo.define("sh_pos_advance_cache.cache_product_attribute_value", function (require) {
    "use strict";

    var indexedDB = require('sh_pos_advance_cache.indexedDB');
    const { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const rpc = require("web.rpc");

    const shPosProductAttributeValueModel = (PosGlobalState) => class shPosProductAttributeValueModel extends PosGlobalState {

       
    }
    Registries.Model.extend(PosGlobalState, shPosProductAttributeValueModel);

});
