/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useRef, onPatched, onMounted, useState } from "@odoo/owl";


//Below Code for Alert while From & To time not enter and Custom Hours Boolean is True
$('#apply_button').click(function () {
    if (($('#request_unit_hours')[0].checked == true) && ($('#request_from')[0].value == '' || $('#request_to')[0].value == '')) {
        alert('Please enter the From: & To: time before Apply Leave.')
        return false
    }
    return true
});
//----------------------



//Below Code for From Date & End Date
var dateFromInput = $('#date_from')[0];
var dateToInput = $('#date_to')[0];
if (dateFromInput && dateToInput) {
    var currentDate = new Date();
    var formattedDate = currentDate.toISOString().split('T')[0];
    dateFromInput.value = formattedDate;
    dateToInput.value = formattedDate;

    var selectedDate = new Date(dateFromInput.value);
    dateToInput.min = selectedDate.toISOString().split('T')[0];
    var currentDateTo = new Date(dateToInput.value);
    if (currentDateTo < selectedDate) {
        dateToInput.value = '';
    };

    dateFromInput.addEventListener("input", function () {
        var selectedDate = new Date(dateFromInput.value);
        dateToInput.min = selectedDate.toISOString().split('T')[0];
        var currentDateTo = new Date(dateToInput.value);
        if (currentDateTo < selectedDate) {
            dateToInput.value = '';
        };
        if (dateFromInput && dateToInput) {
            // Calculation of days between start & end date 
            dateToInput.addEventListener('change', function () {
                var startDate = new Date(dateFromInput.value)
                var endDate = new Date(dateToInput.value)
                var timeDifference = endDate.getTime() - startDate.getTime();
                var daysDifference = timeDifference / (1000 * 60 * 60 * 24);
                daysDifference = Math.round(daysDifference);
                if (daysDifference == 0) {
                    $('.duration_input_class')[0].innerHTML = (daysDifference + 1).toString() + ' Day'
                } else {
                    $('.duration_input_class')[0].innerHTML = (daysDifference + 1).toString() + ' Days'
                }
            })
        }
    });
};
//----------------------

//Below Code for Time Off Type Changed based on that Leave Type is 'Day' ot 'Hours' type
$('#holiday_status_id').on('change', function () {
    var selectedIndex = $('#holiday_status_id')[0].options.selectedIndex
    var selectedType = $('#holiday_status_id')[0].options[selectedIndex].dataset.id
    if (selectedType == 'hour') {
        $('.custom_show_field').removeClass('d-none')
        $('.duration_input_class')[0].innerHTML = '8 Hours'
    } else {
        $('.custom_show_field').addClass('d-none')
        $('.duration_input_class')[0].innerHTML = '1 Day'

    }
});
//------------

//Below code for 'Half Day' & 'Custom Hours' checkbox visibility
$('.custom_show_input').change(function (ev) {
    if (ev.currentTarget.checked) {
        if (ev.currentTarget.id == 'request_unit_half') {
            $('.request_date_from_period').removeClass('d-none')
            $('.date_from').removeClass('col-md-12')
            $('.date_from').addClass('col-md-6')
            $('.duration_input_class')[0].innerHTML = '4 Hours'
        } else {
            $('.request_date_from_period').addClass('d-none')
            $('.date_from').removeClass('col-md-6')
            $('.date_from').addClass('col-md-12')
        }
        $('.date_to').addClass('d-none')
        $('.request_time_from_to').removeClass('d-none')

        var reqFromSelectIndex = $('#request_from')[0].options.selectedIndex
        var reqToSelectIndex = $('#request_to')[0].options.selectedIndex

        if (reqFromSelectIndex == 0 && reqToSelectIndex == 0 && ev.currentTarget.id != 'request_unit_half') {
            $('.duration_input_class')[0].innerHTML = '0 Hours'
        }


        const fromTimeSelect = $('#request_from')[0];
        const toTimeSelect = $('#request_to')[0];
        fromTimeSelect.addEventListener("change", function () {
            const selectedFromTime = this.value; // Get the selected time from "From:"

            // Clear the previously selected options in "To:"
            toTimeSelect.selectedIndex = 0;

            // Disable all options in "To:" that are before the selected "From:" time
            for (let i = 1; i < toTimeSelect.options.length; i++) {
                const optionTime = toTimeSelect.options[i].value;
                // Compare the times in a format suitable for your specific use case
                if (compareTime(selectedFromTime, optionTime) >= 0) {
                    toTimeSelect.options[i].disabled = false;
                } else {
                    toTimeSelect.options[i].disabled = true;
                }
            }

            // Below Calculation for hours difference in Duration
            if (fromTimeSelect && toTimeSelect) {
                toTimeSelect.addEventListener('change', function () {
                    const fromTimeSelectSelectedIndex = $('#request_from')[0].options.selectedIndex;
                    const toTimeSelectSelectedIndex = $('#request_to')[0].options.selectedIndex;
                    const fromValue = $('#request_from')[0].options[fromTimeSelectSelectedIndex].value
                    const ToValue = $('#request_to')[0].options[toTimeSelectSelectedIndex].value
                    $('.duration_input_class')[0].innerHTML = (ToValue - fromValue).toString() + ' Hours'
                })
            }
        });

        function compareTime(time1, time2) {
            if (time1 >= time2) {
                return -1, -1
            } else {
                return 0, 0
            }
        };
    } else {
        $('.date_to').removeClass('d-none')
        $('.request_date_from_period').addClass('d-none')
        $('.date_from').removeClass('col-md-12')
        $('.date_from').addClass('col-md-6')
        $('.request_time_from_to').addClass('d-none')
        $('.duration_input_class')[0].innerHTML = '8 Hours'
    }

    if (ev.currentTarget.checked && ev.currentTarget.id == 'request_unit_half') {
        $('#request_unit_hours').prop('checked', false)
        $('.request_time_from_to').addClass('d-none')
    } else if (ev.currentTarget.checked && ev.currentTarget.id == 'request_unit_hours') {
        $('#request_unit_half').prop('checked', false)
    }
});
//-------------





//export class NewLeavePage extends Component {
//    setup() {
//        super.setup();
//        console.log("-------setup----------")
//        onMounted(this._dateInpute);
//    }
//
//    _dateInpute(ev){
//        console.log("---------------ev-------------")
//    }
//}
//
//NewLeavePage.template = "NewLeavePage";
//
//registry.category("view").add("hr_leave_portal_cr", NewLeavePage);

