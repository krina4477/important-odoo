odoo.define('pos_sale.PharmacyOrderManagementScreen', function (require) {
    'use strict';

    const { sprintf } = require('web.utils');
    const { parse } = require('web.field_utils');
    const { useContext } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const Registries = require('point_of_sale.Registries');
    const PharmacyOrderFetcher = require('pos_sale.PharmacyOrderFetcher');
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const contexts = require('point_of_sale.PosContext');
    const models = require('point_of_sale.models');

    class PharmacyOrderManagementScreen extends ControlButtonsMixin(IndependentToOrderScreen) {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('click-sale-order', this._onClickPharmaOrder);
            useListener('next-page', this._onNextPage);
            useListener('prev-page', this._onPrevPage);
            useListener('search', this._onSearch);
            PharmacyOrderFetcher.setComponent(this);
            this.orderManagementContext = useContext(contexts.orderManagement);
        }
        mounted() {
            PharmacyOrderFetcher.on('update', this, this.render);
            this.env.pos.get('orders').on('add remove', this.render, this);

            const flexContainer = this.el.querySelector('.flex-container');
            const cpEl = this.el.querySelector('.control-panel');
            const headerEl = this.el.querySelector('.header-row');
            const val = Math.trunc(
                (flexContainer.offsetHeight - cpEl.offsetHeight - headerEl.offsetHeight) /
                    headerEl.offsetHeight
            );
            PharmacyOrderFetcher.setNPerPage(val);


            setTimeout(() => PharmacyOrderFetcher.fetch(), 0);
        }
        willUnmount() {
            PharmacyOrderFetcher.off('update', this);
            this.env.pos.get('orders').off('add remove', null, this);
        }
        get selectedClient() {
            const order = this.orderManagementContext.selectedOrder;
            return order ? order.get_client() : null;
        }
        get orders() {
            return PharmacyOrderFetcher.get();
        }
        async _setNumpadMode(event) {
            const { mode } = event.detail;
            this.numpadMode = mode;
            NumberBuffer.reset();
        }
        _onNextPage() {
            PharmacyOrderFetcher.nextPage();
        }
        _onPrevPage() {
            PharmacyOrderFetcher.prevPage();
        }
        _onSearch({ detail: domain }) {
            PharmacyOrderFetcher.setSearchDomain(domain);
            PharmacyOrderFetcher.setPage(1);
            PharmacyOrderFetcher.fetch();
        }
        async _onClickPharmaOrder(event) {
            var self = this;
            const clickedOpd = event.detail;
            const { confirmed, payload: selectedOption } = await this.showPopup('SelectionPopup',
                {
                    title: this.env._t('What do you want to do?'),
                    list: [{id:"0", label: this.env._t("Apply a down payment"), item: false}, {id:"1", label: this.env._t("Settle the order"), item: true}],
                });

            if(confirmed){
                let PosOrder = this.env.pos.get_order();
                let opd_opd = await this._getSaleOrder(clickedOpd.id);
                try {
                    await this.env.pos.load_new_partners();
                }
                catch (error){}
                // Add If condition
                let order_partner = this.env.pos.db.get_partner_by_id(clickedOpd.patient_id[0])
                if(order_partner){
                    PosOrder.set_client(order_partner);
                } else {
                    try {
                        await this.env.pos._loadPartners([opd_opd.patient_id[0]]);
                    }
                    catch (error){
                        const title = this.env._t('Customer loading error');
                        const body = _.str.sprintf(this.env._t('There was a problem in loading the %s customer.'), opd_opd.patient_id[1]);
                        await this.showPopup('ErrorPopup', { title, body });
                    }
                    PosOrder.set_client(this.env.pos.db.get_partner_by_id(opd_opd.patient_id[0]));
                }

                    var opd_id = event.detail.id
                    var product_list = []
                    _.each(self.env.pos.medicine_id, function(medicine){
                        if (medicine.opd_id[0] == opd_id){
                            self.env.pos._addProducts(medicine.medicine_id);
                            _.each(medicine.medicine_id, function(product){
                                product_list.push({
                                    "product": product,
                                    "total_tablets": medicine.total_tablets
                                })
                            })
                        }
                    });

               _.each(product_list, function(val){
                    let new_line = new models.Orderline({}, {
                        pos: self.env.pos,
                        order: self.env.pos.get_order(),
                        product:self.env.pos.db.get_product_by_id(val.product),
                        sale_order_origin_id: clickedOpd,
                    });
                    new_line.set_quantity(val.total_tablets)
                    self.env.pos.get_order().add_orderline(new_line);
                });
                PosOrder.trigger('change');
                this.close();
            }
        }
        async _getSaleOrder(id) {
            let opd_opd = await this.rpc({
                model: 'opd.opd',
                method: 'read',
                args: [[id],['medicine_line_ids','appointment_date','patient_id','doctor_id','state']],
                context: this.env.session.user_context,
              });

            let medicine_line= await this._getMedicineLines(opd_opd[0].medicine_line_ids);
            opd_opd[0].medicine_line_ids = medicine_line;

            return opd_opd[0];
        }

        async _getMedicineLines(ids) {
            let MedicineLines = await this.rpc({
                model: 'pharmacy.prescription',
                method: 'read_converted',
                args: [ids],
                context: this.env.session.user_context,
            });
            return MedicineLines;
        }
    }
    PharmacyOrderManagementScreen.template = 'PharmacyOrderManagementScreen';
    PharmacyOrderManagementScreen.hideOrderSelector = true;

    Registries.Component.add(PharmacyOrderManagementScreen);

    return PharmacyOrderManagementScreen;
});


