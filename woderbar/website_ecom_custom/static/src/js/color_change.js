odoo.define('website_ecom_custom.color', function (require) {
    "use strict";
    $(document).ready(function(){
        var self = this;
        var session = require('web.session');
        /*if (session.user_id){
            $('.dropdown_logout').css('position','absolute');
            $('.find_dein_radio_li_logout').css('position','absolute');
            $('.dropdown_logout').css('right','30%');
            $('.find_dein_radio_li_logout').css('right','45%');

        }
        else{
            $('.dropdown_logout').css('position','absolute');
            $('.find_dein_radio_li_logout').css('position','absolute');
            $('.dropdown_logout').css('right','30%');
            $('.find_dein_radio_li_logout').css('right','45%');
        }*/

        $(document).on('click','.description' ,function(ev){
            $('.description').css('color', '#b09b5f')
            $('.description').css('text-decoration', 'underline')
            $('.technical').css('color', '#000000')
            $('.technical').css('text-decoration', 'none')

        })
        $(document).on('click','.technical' ,function(ev){
            $('.technical').css('color', '#b09b5f')
            $('.technical').css('text-decoration', 'underline')
            $('.description').css('color', '#000000')
            $('.description').css('text-decoration', 'none')

        })

        $(document).on('click','.vehical_model' ,function(ev){
            $('.vehical_model').css('color', '#b09b5f')
            $('.vehical_model').css('text-decoration', 'underline')
            $('.vehical_description').css('color', '#000000')
            $('.vehical_description').css('text-decoration', 'none')
            $('.technical_info').css('color', '#000000')
            $('.technical_info').css('text-decoration', 'none')
        })

        $(document).on('click','.vehical_description' ,function(ev){
            $('.vehical_description').css('color', '#b09b5f')
            $('.vehical_description').css('text-decoration', 'underline')
            $('.vehical_model').css('color', '#000000')
            $('.vehical_model').css('text-decoration', 'none')
            $('.technical_info').css('color', '#000000')
            $('.technical_info').css('text-decoration', 'none')
        })

        $(document).on('click','.technical_info' ,function(ev){
            $('.technical_info').css('color', '#b09b5f')
            $('.technical_info').css('text-decoration', 'underline')
            $('.vehical_description').css('color', '#000000')
            $('.vehical_description').css('text-decoration', 'none')
            $('.vehical_model').css('color', '#000000')
            $('.vehical_model').css('text-decoration', 'none')
        })

        $(document).on('click','.classic_car' ,function(ev){
               $('.find_dein_radio_li_logout').removeClass('visited');
        })
    });

});

