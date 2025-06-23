odoo.define('sh_pos_product_variant.ProductItem', function (require) {
    'use strict';

    const ProductItem = require("point_of_sale.ProductItem");
    const Registries = require("point_of_sale.Registries");

    const { onMounted } = owl

    const PosProductItem = (ProductItem) =>
        class extends ProductItem {
            setup(){
                super.setup()
                onMounted(() => {
                    var self = this;
                    if (self.env.pos.config.sh_pos_enable_product_variants) {
                        var product = this.props.product
                        var variants = product.product_variant_count;
                        if (variants > 1) {
                            _.each($("article[data-product-id='"+   product.id + "']"), function (each) {
                                if (product.id == each.dataset.productId && variants) {
                                    $(each).find('.price-tag').addClass('sh_has_variant');
                                    $(each).find('.price-tag').text(variants + ' variants');
                                }
                            })
                        }
                    }
                });
            }
        }

    Registries.Component.extend(ProductItem, PosProductItem);

})