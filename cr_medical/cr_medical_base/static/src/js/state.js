odoo.define('cr_medical_base.state', function (require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');


    $(document).ready(function () {
        $("select[name=\"country_id\"]").change(function () {
            _onChangeCountry()
        });

        function _onChangeCountry(ev) {
            _changeCountry();
        }

        function _changeCountry() {
            if (!$("#country_id").val()) {
                return;
            }

            ajax.jsonRpc("country_infos/"+ $("#country_id").val(), 'call', {
            }).then(function (data) {
                var selectStates = $("select[name='state_id']");
                if (selectStates.data('init') === 0 || selectStates.find('option').length === 1) {
                    if (data.states.length) {
                        selectStates.html('');
                        _.each(data.states, function (x) {
                            var opt = $('<option>').text(x[1])
                                .attr('value', x[0])
                                .attr('data-code', x[2]);
                            selectStates.append(opt);
                        });
                        selectStates.parent('div').show();
                    } else {
                        selectStates.val('').parent('div').hide();
                    }
                    selectStates.data('init', 0);
                } else {
                    selectStates.data('init', 0);
                }

            });
        }
    });
});