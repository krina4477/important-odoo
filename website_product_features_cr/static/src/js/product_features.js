/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.ProductFeatureAutoLoader = publicWidget.Widget.extend({
    selector: "#wrapwrap",

    start() {
        this._loadFeaturesByProductId(); // ✅ Call on page load
        this._bindVariantChangeEvent();  // ✅ Call on variant change
        return this._super(...arguments);
    },

    _bindVariantChangeEvent() {
        this.$el.on('change', 'input.js_variant_change', () => {
            setTimeout(() => {
                const productId = $('.product_id').val();
                if (productId) {
                    this._loadFeaturesByProductId();
                }
            }, 100);
        });
    },

    async _loadFeaturesByProductId() {
        setTimeout(() => {
            const productId = $('.product_id').val();
            if (!productId) {
                $('#variant-features-body').html(`
                    <div class="text-muted py-3 px-4">No valid variant selected.</div>
                `);
                return;
            }
            const response = rpc("/get_variant_features", {
                product_id: productId,
            }).then(response => {
                console.log("Features loaded successfully:", response);
                const features = response.features || [];

                if (!features.length) {
                    $('#variant-features-body').html(`
                            <div class="text-muted py-3 px-4">No features found for this variant.</div>
                        `);
                    return;
                }

                this._renderFeaturesTable(features);
            });
        }, 300);
    },

    _renderFeaturesTable(features) {
        let html = `
            <div class="d-flex justify-content-center">
                <div class="my-4" style="max-width: 600px; width: 100%;">
                    <div class="card-body p-0">
                        <table class="table mb-0 text-center">
                            <tbody>
                                <tr>
                                    <td colspan="2" class="py-3">
                                        <h3 class="fw-bold mb-0">Product Features</h3>
                                    </td>
                                </tr>
        `;

        features.forEach(item => {
            html += `
                <tr class="border-bottom hover-row">
                    <td class="py-3 px-4 text-muted text-uppercase small fw-semibold" style="width: 40%;">${item.feature_name}</td>
                    <td class="py-3 px-4 text-dark">${item.feature_values}</td>
                </tr>
            `;
        });

        html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

        $('#variant-features-body').html(html);
    }
});
