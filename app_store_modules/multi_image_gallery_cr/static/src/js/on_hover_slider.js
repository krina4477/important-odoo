/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.websiteSaleCarouselProduct = publicWidget.registry.websiteSaleCarouselProduct.extend({
    /**
     * @override
     */
    async start() {
        await this._super(...arguments);
        this._bind3DButtonClick();
        console.log("**********thisis websitesale shop page********8")

        this.$el.find('.o_image_64_cover, .o_product_video_thumb').on('mouseenter', this._onItemHover.bind(this));
        this.$el.find('.o_image_64_cover, .o_product_video_thumb').on('mouseleave', this._onItemLeave.bind(this));
    },
    
    _bind3DButtonClick: function () {
        console.log("------------");
        
    },

    _onItemHover(ev) {
        const $item = $(ev.currentTarget);  
        console.log('Hover on:***********',$item);
        ev.preventDefault();
        $item.click();
        
    },

    _onItemLeave(ev) {
        const $item = $(ev.currentTarget);
        $item.css('transform', 'scale(1)');
    }
});