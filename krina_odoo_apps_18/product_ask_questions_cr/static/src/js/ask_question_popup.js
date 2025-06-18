/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";


publicWidget.registry.ask_question_popup = publicWidget.Widget.extend({
    selector: '.o_wsale_product_page',
    events: Object.assign({}, publicWidget.Widget.prototype.events,
    {
        'click .js_send_question': '_js_send_question',
    }),

    _js_send_question: async function(e)
    {
        var name = $('#first-name').val();
        var email_name = $('#email').val();
        var product_name = $('#product_name').val();
        var partner_id = $('#partner_id').val();
        var phone_no = $('#phone').val();
        var question = $('#question').val();
        var details = $('#details').val();
        if (name || email_name || product_name || partner_id || phone_no || question || details)
        {
            rpc('/create/crm/lead',
            {
                'name': name,
                'email_name': email_name,
                'product_name': product_name,
                'partner_id': parseInt(partner_id),
                'phone_no': phone_no,
                'question': question,
                'details': details,
            }).then(function (data)

            {
                if (data.result){
                    alert("Your question related to product has been submitted successfully.!!")
                    location.reload()
                }
                else
                {
                    alert("Something went wrong, please try after sometime.")
                    location.reload()
                }
            });
            window.close()
            return false;
        }
    }
});


$(document).ready(function($){
    var $cf = $('#phone');
    $cf.blur(function(e){
        var phone = $(this).val();
        if (isNaN(phone))
        {
            alert('Please enter a valid phone number!!');
            $('#phone').val('');
        }
    });
});