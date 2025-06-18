/* @odoo-module */

import { rpc } from "@web/core/network/rpc";

$(document).ready(function() {
    $('#js_send_demo_req').click(async function(e) {
        var name = $('#first-name').val();
        var email_name = $('#email').val();
        var product_name = $('#product_name').val();

        var details = $('#details').val();
        if (name || email_name || product_name || details) {
            try {
                var data = await rpc('/thankyou_page', {
                    'name': name,
                    'email_name': email_name,
                    'product_name': product_name,
                    'details': details,
                });
                if (data.result) {
                    location.href = "/thankyou";
                } else {
                    location.href = "/tryagain";
                }
            } catch (error) {
                console.error(error);
            }
        }
        return false;
    });
});
