odoo.define('cr_medical_base.days_existpatient', function (require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');


    $(document).ready(function () {
        $("select[name=doctor_id]").change(function () {

            if (!$("#doctor_id").val()) {
                return;
            }

            ajax.jsonRpc("/test/day_infos/", 'call', {
                'doctor_data':$("#doctor_id").val()
            }).then(function (data) {

                var selectDays = $("select[name='availabel_days']");
                if (selectDays.data('init') === 0 || selectDays.find('option').length === 1) {
                    if (data.days.length) {
                        selectDays.html('');
                        var blankopt = $('<option>').text('')
                        selectDays.append(blankopt);
                        _.each(data.days, function (x) {
                            var opt = $('<option>').text(x[1])
                            .attr('value', x[0])
                            .attr('data-code', x[2]);

                            selectDays.append(opt);
                        });
                        selectDays.parent('div').show();
                    } else {
                        selectDays.val('').parent('div').hide();
                    }
                    selectDays.data('init', 0);
                } else {
                    selectDays.data('init', 0);
                }

            });
        });
    });
});