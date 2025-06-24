odoo.define('pos_sale.PharmacyOrderManagementControlPanel', function (require) {
    'use strict';

    const { useContext } = owl.hooks;
    const { useAutofocus, useListener } = require('web.custom_hooks');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const PharmacyOrderFetcher = require('pos_sale.PharmacyOrderFetcher');
    const contexts = require('point_of_sale.PosContext');


    const VALID_SEARCH_TAGS = new Set(['date', 'patient_id','name']);
    const FIELD_MAP = {
//        date: 'appointment_date',
//        patient_id: 'patient_id',
//        client: 'medicine_line_ids.indication_id',
//        name: 'medicine_line_ids.medicine_id',
//        order: 'medicine_line_ids.dose'
    };
    const SEARCH_FIELDS = ['appointment_date', 'patient_id.name'];

    class PharmacyOrderManagementControlPanel extends PosComponent {
        constructor() {
            super(...arguments);

            this.orderManagementContext = useContext(contexts.orderManagement);
            useListener('clear-search', this._onClearSearch);
            useAutofocus({ selector: 'input' });

            let currentClient = this.env.pos.get_client();
            if (currentClient) {
                this.orderManagementContext.searchString = currentClient.name;
                let domain = this._computeDomain();
                PharmacyOrderFetcher.setSearchDomain(domain);
            }
        }
        onInputKeydown(event) {
            if (event.key === 'Enter') {
                this.trigger('search', this._computeDomain());
            }
        }
        get showPageControls() {
            return PharmacyOrderFetcher.lastPage > 1;
        }
        get pageNumber() {
            const currentPage = PharmacyOrderFetcher.currentPage;
            const lastPage = PharmacyOrderFetcher.lastPage;
            return isNaN(lastPage) ? '' : `(${currentPage}/${lastPage})`;
        }
        get validSearchTags() {
            return VALID_SEARCH_TAGS;
        }
        get fieldMap() {
            return FIELD_MAP;
        }
        get searchFields() {
            return SEARCH_FIELDS;
        }

        _computeDomain() {
            let domain = [['state', '!=', 'cancel']];
            const input = this.orderManagementContext.searchString.trim();
            if (!input) return domain;

            const searchConditions = this.orderManagementContext.searchString.split(/[,&]\s*/);
            if (searchConditions.length === 1) {
                let cond = searchConditions[0].split(/:\s*/);
                if (cond.length === 1) {
                  domain = domain.concat(Array(this.searchFields.length - 1).fill('|'));
                  domain = domain.concat(this.searchFields.map((field) => [field, 'ilike', `%${cond[0]}%`]));
                  return domain;
                }
            }

            for (let cond of searchConditions) {
                let [tag, value] = cond.split(/:\s*/);
                if (!this.validSearchTags.has(tag)) continue;
                domain.push([this.fieldMap[tag], 'ilike', `%${value}%`]);
            }
            return domain;
        }
        _onClearSearch() {
            this.orderManagementContext.searchString = '';
            this.onInputKeydown({ key: 'Enter' });
        }
    }
    PharmacyOrderManagementControlPanel.template = 'PharmacyOrderManagementControlPanel';

    Registries.Component.add(PharmacyOrderManagementControlPanel);

    return PharmacyOrderManagementControlPanel;
});
