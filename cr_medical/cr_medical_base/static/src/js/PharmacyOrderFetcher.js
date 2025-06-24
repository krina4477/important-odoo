odoo.define('pos_sale.PharmacyOrderFetcher', function (require) {
    'use strict';

    const { EventBus } = owl.core;
    const { Gui } = require('point_of_sale.Gui');
    const { isConnectionError } = require('point_of_sale.utils');
    const models = require('point_of_sale.models');

    class PharmacyOrderFetcher extends EventBus {
        constructor() {
            super();
            this.currentPage = 1;
            this.ordersToShow = [];
            this.totalCount = 0;
        }

        get lastPage() {
            const nItems = this.totalCount;
            return Math.trunc(nItems / (this.nPerPage + 1)) + 1;
        }

        async fetch() {
            try {
                let limit, offset;
                let start, end;
                // Show orders from the backend.
                offset =
                    this.nPerPage +
                    (this.currentPage - 1 - 1) *
                        this.nPerPage;
                limit = this.nPerPage;
                this.ordersToShow = await this._fetch(limit, offset);

                this.trigger('update');
            } catch (error) {
                if (isConnectionError(error)) {
                    Gui.showPopup('ErrorPopup', {
                        title: this.comp.env._t('Network Error'),
                        body: this.comp.env._t('Unable to fetch orders if offline.'),
                    });
                    Gui.setSyncStatus('error');
                } else {
                    throw error;
                }
            }
        }

        async _fetch(limit, offset) {
            const pharma_orders = await this._getOrderIdsForCurrentPage(limit, offset);
            this.totalCount = pharma_orders.length;
            return pharma_orders;
        }
        async _getOrderIdsForCurrentPage(limit, offset) {
//            let domain = [[]].concat(this.searchDomain || []);
            return await this.rpc({
                model: 'opd.opd',
                method: 'search_read',
                args: [[],['name','appointment_date','patient_id','doctor_id','state','medicine_line_ids']],
                context: this.comp.env.session.user_context,
            });
        }

        nextPage() {
            if (this.currentPage < this.lastPage) {
                this.currentPage += 1;
                this.fetch();
            }
        }
        prevPage() {
            if (this.currentPage > 1) {
                this.currentPage -= 1;
                this.fetch();
            }
        }
        /**
         * @param {integer|undefined} id id of the cached order
         * @returns {Array<models.Order>}
         */
        get(id) {
            return this.ordersToShow;
        }
        setSearchDomain(searchDomain) {
            this.searchDomain = searchDomain;
        }
        setComponent(comp) {
            this.comp = comp;
            return this;
        }
        setNPerPage(val) {
            this.nPerPage = val;
        }
        setPage(page) {
            this.currentPage = page;
        }

        async rpc() {
            Gui.setSyncStatus('connecting');
            const result = await this.comp.rpc(...arguments);
            Gui.setSyncStatus('connected');
            return result;
        }
    }

    return new PharmacyOrderFetcher();
});
