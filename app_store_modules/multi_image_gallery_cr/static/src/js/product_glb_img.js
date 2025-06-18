import { rpc } from "@web/core/network/rpc";
import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.WebsiteSale.include({
    /**
     *
     * @override
     * 
     */
    start: function (ev) {
        this._super.apply(this, arguments);
        this._bind3DButtonClick();
        // this._bindCloseModal();
        const vari = document.getElementsByClassName('css_attribute_color')
        console.log("---------- vari", vari);
        // console.log("---------- data.glb_image_url", ev.session.glb_image_url);
    },

    _bind3DButtonClick: function () {
        const self = this;
        $(document).on('click', 'li[data-bs-target="#product3DModal"]', function () {
            const product_id = self.last_combination_product_id;
            if (!product_id) return;
        
            const $container = $("#product-3d-container").html('Loading 3D...');
            rpc("/get/product/files", {
                product_id,
            }).then((data) => {
                console.log("++++++++++data",data);
                const html = `
                    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                    <model-viewer
                        src="${data.glb_image_url}"
                        alt="3D Product"
                        shadow-intensity="1"
                        camera-controls
                        auto-rotate
                        style="width: 100%; height: 500px; background-color: #fff;">
                    </model-viewer>`;
                $container.html(html);
                $("#product3DModal").modal("show");
            });
            
            // $('.css_attribute_color').addClass('d-none'); 
        });

        // $('#product3DModal').on('click', function () {
        //     $('header, .oe_search_button, .o_header_affix').hide();
        // });
        
        // $('#product3DModal').on('hidden.bs.modal', function () {
        //     $('header, .o_main_navbar, .o_header_affix').show();
        // });
        
        
        // $(document).on('click', '.view-3d-modal', function () {
        //     const product_id = self.last_combination_product_id; // We'll save this when combination changes
        //     if (!product_id) {
        //         alert("No product selected.");
        //         return;
        //     }
        //     const $container = $("#product-3d-container");
        //     $container.html('<p>Loading 3D view...</p>');
        //     rpc("/get/product/files", { 
        //         product_id: product_id,
        //     }).then((data) => {
        //         console.log("---------- data.glb_image_url", data.glb_image_url);
                
        //         const glb_image_url = data.glb_image_url || 'N/A';
        //         const variant_name = data.variant_name || 'N/A';

        //         const html = `
        //             <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
        //             <model-viewer
        //                 src="${glb_image_url}"
        //                 alt="3D Product"
        //                 shadow-intensity="1"
        //                 camera-controls
        //                 auto-rotate
        //                 style="width: 100%; height: 500px; background-color: #fff;">
        //             </model-viewer>
        //             <div class="p-3">
        //                 Product Variant: <strong>${variant_name}</strong>
        //             </div>
        //         `;
        //         $container.html(html);
        //         $("#product3DModal").modal("show");
        //     });
        // });
    },

    // _bindCloseModal: function () {
    //     console.log("++++++++=in close btn");
    //     $('.css_attribute_color').removeClass('d-none'); 
    // },

    async _onChangeCombination(ev, $parent, combination) {
        this._super.apply(this, arguments);
        this.last_combination_product_id = combination.product_id;
        console.log("***********ev",ev);
        // console.log("***********ev",ev.target.form[1].defaultValue);
        $('#product3DModal').on('show.bs.modal', function () {
            console.log("+++++++++++++++show model");
            $('.css_attribute_color').addClass('d-none');
            $('.css_quantity').addClass('d-none');
            $('.oe_search_button').addClass('d-none');
            $('.o_wsale_product_attribute').addClass('d-none');
        });
        $('#product3DModal').on('hidden.bs.modal', function () {
            console.log("+++++++++++++++hide model");
            $('.css_attribute_color').removeClass('d-none');
            $('.css_quantity').removeClass('d-none');
            $('.oe_search_button').removeClass('d-none');
            $('.o_wsale_product_attribute').removeClass('d-none');
        });
        
        const $btn = $("#view-3d-button");
        console.log("++++++++$btn",$btn);
        // rpc("/get/product/files", {
        //     product_id: combination.product_id,
        // }).then((data) => {
        //     console.log("++++++++++++data",data);
        //     console.log("++++++++++++data.variant_id",data.variant_id);
            
        //     if (data.variant_id) {
        //         $btn.show();
        //     } else {
        //         $btn.hide();
        //     }
        // });
    }
});