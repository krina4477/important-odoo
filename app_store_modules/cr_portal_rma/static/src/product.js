/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';
import { rpc } from "@web/core/network/rpc";
import { cartHandlerMixin } from '@website_sale/js/website_sale_utils';
import { WebsiteSale } from '@website_sale/js/website_sale';
import { _t } from "@web/core/l10n/translation";

publicWidget.registry.AddToCartSnippetCustom = WebsiteSale.extend(cartHandlerMixin, {
    selector: '.return_button',
    events: {
        'click': '_onClickReturnButton',
//        'submit': '_onSubmit',
    },

    init() {
        this._super(...arguments);

    },

    _onClickReturnButton: async function (ev) {
        console.log("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",ev);
        const orderId = $(ev.currentTarget).data('order-id');
        var picking_id = $(ev.currentTarget).data('picking-id');
        console.log("ORDERRRRRRRRRRRRRRRRRRRRRRRRRRRRR", orderId,$('#returnModal'))
        const isAddToCartAllowed = await rpc(`/portal/order/return_lines`, {
                order_id: orderId,
                picking_id: picking_id,
        }).then(data => {
                const modalBody = $('#return_product_lines').empty();

                data.lines.forEach(line => {
                    modalBody.append(`
                        <div class="mb-2">
                            <label>${line.product_name} (Delivered: ${line.qty_delivered})</label>
                            <input type="number" name="line_${line.line_id}" max="${line.qty_delivered}" min="1" value="1" class="form-control" />
                        </div>
                    `);
                });

                $('#returnModal').data('picking-id', picking_id).modal('show');

         });
  },

});

publicWidget.registry.AddToCartSnippetCustomReturn = WebsiteSale.extend(cartHandlerMixin, {
    selector: '.js_website_return_submit_form',
    events: {
        'click': '_onSubmit',
    },
    init() {
        this._super(...arguments);

    },

    _onSubmit: async function (ev) {
        ev.preventDefault();  // Prevent default form submission behavior

    let returnData = {};

    // Select all input elements inside the modal body
        $('#returnModal input[type="number"]').each(function () {
            const name = $(this).attr('name');  // e.g., line_123
            const value = parseFloat($(this).val());

            // Only include lines with a value > 0
            if (value > 0) {
                returnData[name] = value;
            }
        });
        var order_id = $('.return_button').data('order-id')
        var picking_id = $('#returnModal').data('picking-id')
        console.log("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR",picking_id)
        if (order_id && returnData){
            const isAddToCartAllowed = await rpc(`/portal/return_order/order_create`, {
                order_id: order_id,
                picking_id: picking_id,
                lines: returnData,
            }).then(data => {
                    console.log("UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU");
                    $('#returnModal').modal('hide');

                    // Show the success modal
                    $('#successReturnModal').modal('show');

             });
        }


        console.log("Return data to submit:", returnData);
        console.log("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",ev);

    },

});
$(document).on('click', '.return_success', function () {
    window.location.reload();
});
export default publicWidget.registry.AddToCartSnippetCustom;
export default publicWidget.registry.AddToCartSnippetCustomReturn;
