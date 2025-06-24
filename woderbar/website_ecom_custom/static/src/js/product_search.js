odoo.define('website_ecom_custom.product_search', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    var core = require('web.core');
    var QWeb = core.qweb;
    var ajax = require('web.ajax');

    $(document).ready(function(){
        var x_radio_values = []
        var self = this;
        $(document).on('click','.feature_class' ,function(ev){
              var attrib_val = $('.feature_class').val();
              $(ev.currentTarget).closest("form").submit();
        })

        $(document).on('click','.categ_class' ,function(ev){
            console.log("Onclick Method called")
            // debugger
              var attrib_val = $('.categ_class').val();
              $(ev.currentTarget).closest("form").submit();
        })

         $(document).on('change','.modal_year_class' ,function(ev){
              var attrib_val = $('.modal_year_class').val();
              $(ev.currentTarget).closest("form").submit();
        })

        $(document).on('change','.model_class' ,function(ev){
              var attrib_val = $('.model_class').val();
              $(ev.currentTarget).closest("form").submit();
        })

        $(document).on('click','.manufacturer_class' ,function(ev){
              var attrib_val = $('.manufacturer_class').val();
              $(ev.currentTarget).closest("form").submit();
        })


        $(document).on('change','.manufact_select_class' ,function(ev){
            var attrib_val = $('.manufact_select_class option:selected').val();
            ajax.jsonRpc('/find_model_year', 'call', {
                'manufacturer_value': attrib_val,
            }).then(function (result) {
                var selectBaujahr = $("select[name='model_year']");
                if (result.Baujahr.length) {
                    selectBaujahr.html('');
                    selectBaujahr.append('<option value="" class="option_manu">Baujahr</option>')
                    _.each(result.Baujahr, function (x) {
                        var opt = $('<option>').text(x[1]).attr('value', x[0]);
                        selectBaujahr.append(opt);
                    });
                }
            });

        });

        $(document).on('change','.year_select_class' ,function(ev){
            var Fahrzeug_val = $('.manufact_select_class option:selected').val();
            var Baujahr_val = $('.year_select_class option:selected').val();
            ajax.jsonRpc('/find_model_name', 'call', {
                'Fahrzeug_val': Fahrzeug_val,
                'Baujahr_val': Baujahr_val,
            }).then(function (result) {
                var selectModell = $("select[name='model_name']");
                if (result.Modell.length) {
                    selectModell.html('');
                    selectModell.append('<option value="" class="option_manu">Modell</option>')
                    _.each(result.Modell, function (x) {
                        var opt = $('<option>').text(x[1]).attr('value', x[0]);
                        selectModell.append(opt);
                    });
                }
            });
        });
    });

});

