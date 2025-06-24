odoo.define('cr_medical_base.selecttime_existpatient', function (require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');


    $(document).ready(function () {
        $("select[name=availabel_days]").on('change',function () {
            ajax.jsonRpc("/test/selecttime_infos/", 'call', {
            'availabel_days':$("#availabel_days").val(),
            'doctor_data':$("#doctor_id").val()
            }).then(function (data) {
                var selecttimeid = $("select[name='select_time_id']");
                if (selecttimeid.data('init') === 0 || selecttimeid.find('option').length === 1) {
                    if (data.selecttime.length) {
                        selecttimeid.html('');
                        var blankopt = $('<option>').text('')
                        selecttimeid.append(blankopt);
                        _.each(data.selecttime, function (x) {
                            var opt = $('<option>').text(x[1])
                            .attr('value', x[0])
                            selecttimeid.append(opt);
                        });
                        selecttimeid.parent('div').show();
                    } else {
                        selecttimeid.val('').parent('div').hide();
                    }
                    selecttimeid.data('init', 0);
                } else {
                    selecttimeid.data('init', 0);
                }
            });
        });
    });
});