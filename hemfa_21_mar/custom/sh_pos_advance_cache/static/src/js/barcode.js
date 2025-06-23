odoo.define("sh_pos_advance_cache.cache_product_barcode", function (require) {
    "use strict";

    var indexedDB = require('sh_pos_advance_cache.indexedDB');
    const { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const rpc = require("web.rpc");

    const shPosProductUomModel = (PosGlobalState) => class shPosProductUomModel extends PosGlobalState {

        async _processData(loadedData) {
            const session_id = odoo.pos_session_id;
        
            // Helper function to load data from IndexedDB or RPC
            const loadData = async (model, cacheKey, rpcMethod) => {
                const dynamicKey = `${session_id}_${model}`;
                let data = [];
        
                // Check if data is already loaded from localStorage
                if (localStorage.getItem(dynamicKey) === 'loaded') {
                    // Load from IndexedDB
                    data = await indexedDB.get_all(cacheKey);
                } else {
                    // Load from RPC and cache in IndexedDB
                    await this.env.services.rpc({
                        model: 'pos.session',
                        method: rpcMethod,
                        args: [odoo.pos_session_id, model],
                    }).then((result) => {
                        if (result) {
                            data = result;
                            indexedDB.save_data(cacheKey, data);
                        }
                    });
                    localStorage.setItem(dynamicKey, 'loaded');
                }
        
                // Process and return the required mappings
                const byId = {};
                const byName = {};
                data.forEach((item) => {
                    byId[item.id] = item;
                    if (item.name) byName[item.name] = item;
                });
                return { data, byId, byName };
            };
        
            // Product Barcode
            const productBarcode = await loadData('product.template.barcode', 'product.template.barcode', 'sh_load_model');
            loadedData['product.template.barcode'] = productBarcode.data;
            loadedData['product_by_barcode'] = productBarcode.byId;
            loadedData['barcode_by_name'] = productBarcode.byName;
        
            // Customer (Partner)
            const partner = await loadData('res.partner', 'res.partner', 'sh_load_model');
            loadedData['res.partner'] = partner.data;
        
            // Product Attribute Value
            const attributeValue = await loadData('product.template.attribute.value', 'product.template.attribute.value', 'sh_load_model');
            loadedData['product.template.attribute.value'] = attributeValue.data;
            loadedData['product_temlate_attribute_by_id'] = attributeValue.byId;
        
            const attributesByPtalId = {};
            attributeValue.data.forEach((value) => {
                const attributeLineId = value.attribute_line_id;
                const data = {
                    id: value.product_attribute_value_id,
                    name: value.name,
                    is_custom: value.is_custom,
                    html_color: value.html_color,
                    price_extra: value.price_extra,
                };
        
                if (attributesByPtalId[attributeLineId]) {
                    attributesByPtalId[attributeLineId].values.push(data);
                } else {
                    attributesByPtalId[attributeLineId] = {
                        id: value.attribute_line_id,
                        name: value.display_name.split(":")[0],
                        display_type: value.display_type,
                        values: [data],
                    };
                }
            });
            loadedData['attributes_by_ptal_id'] = attributesByPtalId;
        
            // UOM (Units of Measure)
            const uom = await loadData('uom.uom', 'uom.uom', 'sh_load_model');
            loadedData['uom.uom'] = uom.data;
            loadedData['units_by_id'] = uom.byId;
        
            // Pricelist
            const pricelist = await loadData('product.pricelist', 'product.pricelist', 'sh_load_model');
            loadedData['product.pricelist'] = pricelist.data;
        
            const pricelistDict = await this.env.services.rpc({
                model: 'pos.session',
                method: 'sh_load_model2',
                args: [odoo.pos_session_id, pricelist.data],
            });
            loadedData['default_pricelist'] = pricelistDict.default_pricelist;
            loadedData['all_pricelists'] = pricelistDict.all_pricelists;
            loadedData['all_pricelists_item'] = pricelistDict.all_pricelists_item;
            loadedData['pricelist_item_by_id'] = pricelistDict.pricelist_item_by_id;
            loadedData['pricelist_by_id'] = pricelistDict.pricelist_by_id;
        
            // Pre Define Note
            const preDefine = await loadData('pre.define.note', 'pre.define.note', 'sh_load_model');
            loadedData['pre.define.note'] = preDefine.data;
            loadedData['pre_defined_note_data_dict'] = preDefine.byId;
            loadedData['all_note_names'] = preDefine.byName;
        
            // Product
            const product = await loadData('product.product', 'product.product', 'sh_load_model');
            loadedData['product.product'] = product.data;
        
            // Country
            const country = await loadData('res.country', 'res.country', 'sh_load_model');
            loadedData['res.country'] = country.data;
        
            // State
            const state = await loadData('res.country.state', 'res.country.state', 'sh_load_model');
            loadedData['res.country.state'] = state.data;
        
            // Product Attribute Line
            const attributeLine = await loadData('product.template.attribute.line', 'product.template.attribute.line', 'sh_load_model');
            loadedData['product.template.attribute.line'] = attributeLine.data;
            loadedData['product_temlate_attribute_line_by_id'] = attributeLine.byId;
        
            await super._processData(...arguments);
        }
        
    }
    Registries.Model.extend(PosGlobalState, shPosProductUomModel);

});
