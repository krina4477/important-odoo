odoo.define("sh_pos_advance_cache.indexedDB", function (require) {
    "use strict";

    if (!window.indexedDB) {
        return;
    }

    const indexedDB = window.indexedDB;

    var indexedDB_dic = {

        create_objectstore: function (objectstore) {

            const request = indexedDB.open(odoo.pos_session_id, 1);

            request.onerror = function (event) {
                console.error(`Database error: ${event.target.errorCode}`);
            };

            request.onupgradeneeded = function (event) {

                let db = event.target.result;
                db.createObjectStore('product.product', { keyPath: "id" });
                db.createObjectStore('product.template.attribute.value', { keyPath: "id" });
                db.createObjectStore('product.template.attribute.line', { keyPath: "id" });
                db.createObjectStore('res.partner', { keyPath: "id" });
                db.createObjectStore('res.country', { keyPath: "id" });
                db.createObjectStore('res.country.state', { keyPath: "id" });
                db.createObjectStore('pre.define.note', { keyPath: "id" });
                db.createObjectStore('uom.uom', { keyPath: "id" });
                db.createObjectStore('product.pricelist', { keyPath: "id" });
                db.createObjectStore('product.template.barcode', { keyPath: "id" });
            };

            return request;
        },

        save_data: function (objectstore, data_list) {

            this.create_objectstore(objectstore).onsuccess = function (ev) {
                var db = ev.target.result;
                var txn = db.transaction(objectstore, 'readwrite');
                var store = txn.objectStore(objectstore);

                _.each(data_list, function (each_data) {

                    // Remove non-serializable fields before storing
                    if (objectstore === 'product.product') {
                        _.each(each_data, function (value, key) {
                            if (key === 'pos' || typeof value === 'function') {
                                delete each_data[key];  // Remove non-serializable fields
                            }
                        });
                    }

                    // Deep clone to ensure the data is serializable
                    try {
                        var serializable_data = JSON.parse(JSON.stringify(each_data));
                        var query = store.put(serializable_data);

                        query.onsuccess = function (event) {
//                            console.log("Data successfully stored:", serializable_data);
                        };

                        query.onerror = function (event) {
//                            console.error("Data save error:", event.target.errorCode);
                        };

                    } catch (e) {
//                        console.error("Error serializing data:", e);
                    }

                    txn.oncomplete = function () {
                        db.close();
                    };
                });
            };
        },

        get_all: function (objectstore) {
            var def = new $.Deferred();

            this.create_objectstore(objectstore).onsuccess = function (ev) {
                var db = ev.target.result;
                var txn = db.transaction(objectstore, 'readwrite');
                var store = txn.objectStore(objectstore);

                store.getAll().onsuccess = function (event) {
                    let cursor = event.target.result;
                    def.resolve(cursor);
                };
            };
            return def;
        },

        get_by_id: function (objectstore, key) {
            var def = new $.Deferred();

            this.create_objectstore(objectstore).onsuccess = function (ev) {
                var db = ev.target.result;
                var txn = db.transaction(objectstore, 'readwrite');
                var store = txn.objectStore(objectstore);

                store.get(key).onsuccess = function (event) {
                    let cursor = event.target.result;
                    def.resolve(cursor);
                };
            };
            return def;
        },

        delete_item: function (objectstore, key) {
            var def = new $.Deferred();

            this.create_objectstore(objectstore).onsuccess = function (ev) {
                var db = ev.target.result;
                var txn = db.transaction(objectstore, 'readwrite');
                var store = txn.objectStore(objectstore);

                store.delete(key).onsuccess = function (event) {
                    let cursor = event.target.result;
                    def.resolve(cursor);
                };
            };
            return def;
        },
    };

    return indexedDB_dic;
});
