odoo.define("sh_pos_advance_cache.cache_uom", function (require) {
    "use strict";

    var indexedDB = require('sh_pos_advance_cache.indexedDB');
    const { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const rpc = require("web.rpc");

    const shPosProductUomModel = (PosGlobalState) => class shPosProductUomModel extends PosGlobalState {

        // async _processData(loadedData) {
           
        //     await super._processData(...arguments);
        // }
    }
    Registries.Model.extend(PosGlobalState, shPosProductUomModel);

});
