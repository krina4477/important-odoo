    odoo.define("sh_pos_advance_cache.cache_state", function (require) {
    "use strict";

    var indexedDB = require('sh_pos_advance_cache.indexedDB');
    const { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const rpc = require("web.rpc");

    const shPosCountryStateModel = (PosGlobalState) => class shPosCountryStateModel extends PosGlobalState {

      
    }
    Registries.Model.extend(PosGlobalState, shPosCountryStateModel);

});
