odoo.define("sh_pos_all_in_one_retail.models", function (require) {
    "use strict";

    const { PosGlobalState} = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosOrderSyncGlobalState = (PosGlobalState) => class PosOrderSyncGlobalState extends PosGlobalState {
        async _processData(loadedData) {
            await super._processData(loadedData)
            if(loadedData && loadedData['posted_session']){
                this.db.posted_session_ids = loadedData['posted_session'];
            }
        }
    }
    Registries.Model.extend(PosGlobalState, PosOrderSyncGlobalState);

});
