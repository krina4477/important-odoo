odoo.define('cr_medical_base.multi', function (require) {
    'use strict';
    var rpc = require('web.rpc');

    $(document).ready(function () {

        // Existing Patient Appointment in Confirmation Ref thought Fetch Patine Name
        $("#confirmation_ref").on('input',function () {
            rpc.query({
                route: "/test/patient_id",
                params: {confirmation_ref: $("#confirmation_ref").val()},
            }).then(function (data) {
                var selectStates = $("select[name='patient_name']");
                if (data.states.length) {
                    selectStates.html('');
                    _.each(data.states, function (x) {
                        var opt = $('<option>').text(x[1])
                            .attr('value', x[0])

                        selectStates.append(opt);
                    });
                    selectStates.parent('div').show();
                }
                selectStates.data('init', 0);
            });
        });

        // Check Email Id In Patient
        $("#email").on('change',function () {
            rpc.query({
                route: "/test/email",
                params: {email: $("#email").val()},
            }).then(function (data) {
                if (data){
                    alert('Email must be Unique !!!');
                }
            });
        });

        // Check Email Id In Doctor
        $("#email_id").on('change',function () {
            rpc.query({
                route: "/test/email",
                params: {email: $("#email_id").val()},
            }).then(function (data) {
                if (data){
                    alert('Email must be Unique !!!');
                }
            });
        });

        // Check Licence Id In Doctor
        $("#licence_id").on('change',function () {
            rpc.query({
                route: "/test/licence_id",
                params: {licence_id: $("#licence_id").val()},
            }).then(function (data) {
                if (data){
                    alert('Licence Id must be Unique !!!');
                }
            });
        });

    });
});


$(document).ready(function () {


    $('select').each(function () {
        $(this).select2({
          theme: 'bootstrap4',
          width: 'style',
          placeholder: $(this).attr('placeholder'),
          allowClear: Boolean($(this).data('allow-clear')),
        });
    });

//    Total Time Calculate from Doctor
    $("#from_time,#to_time").on('change',function () {
        var terms = " ";
        if ($("#from_time").val() != "") {
            terms = $("#from_time").val() + ' to ' + $("#to_time").val();
        } else terms = "No time entered";
        $("#total_time_name").val(terms);
    });

    if (window.location.pathname == '/'){
        $('.nav-link').addClass('home-menu')
    }

    $('input[type="radio"]').click(function() {
        var inputValue = $(this).attr("value");
        var targetBox = $("." + inputValue);
        $(".selectt").not(targetBox).hide();
        $(targetBox).show();
    });

//  Mobile Number Check Digits Number in Patient
    $mobile = $('#mobile');
    $mobile.blur(function(e){
        phone = $(this).val();
        phone = phone.replace(/[^0-9]/g,'');
        if (phone.length != 10 && phone.length > 0)
        {
            alert('Phone number must be 10 digits.');
            $('#mobile').val('');
        }
    });

//  Mobile Number Check Digits Number in Doctor
    $mobile1 = $('#mobile1');
    $mobile1.blur(function(e){
        phone = $(this).val();
        phone = phone.replace(/[^0-9]/g,'');
        if (phone.length != 10  && phone.length > 0)
        {
            alert('Phone number must be 10 digits!!!.');
            $('#mobile1').val('');
        }
    });

//  Zip Code Number Check 6 Digits
//    $zip = $('#zip');
//    $zip.blur(function(e){
//        zip_code = $(this).val();
//        zip_code = zip_code.replace(/[^0-9]/g,'');
//        if (zip_code.length != 6 && zip_code.length > 0)
//        {
//            alert('Zip Code Must Be 6 digits.');
//            $('#zip').val('');
//        }
//    });
});


function validation1() {
    var UserDate = document.getElementById("date_of_joining").value;
    var ToDate = new Date();

    if (new Date(UserDate).getTime() >= ToDate.getTime()) {
         alert('Enter Correct Date Of Joining');

          return false;
     }
    return true;
}

function validation() {
    var UserDate = document.getElementById("date_of_birth").value;
    var ToDate = new Date();
    if (new Date(UserDate).getTime() >= ToDate.getTime()) {
         alert('Enter Correct BirthDate');

          return false;
     }
    return true;
}

function comp(){
   var bday = document.getElementById('date_of_birth').value;
    var today = new Date();
    var birthDate = new Date(bday);

    var age = today.getFullYear() - birthDate.getFullYear();
    var m = today.getMonth() - birthDate.getMonth();
    if (today.getMonth() <= birthDate.getMonth() || (today.getMonth() == birthDate.getMonth() && today.getDate() < birthDate.getDate())) {
        age--;
         }

    var month = today.getMonth() - birthDate.getMonth()
    var day = today.getDate() - birthDate.getDate()

    if (age > 0){
        document.getElementById('age').value=age;
    }else{
        document.getElementById('age').value= 0;
    }

}

function myFunction() { //datetoday and compare(exist)
    var a = document.getElementById("appointment_date").value;
    var availabel_day_time = document.getElementById("availabel_days").value;
    var availabel_day = availabel_day_time.split(',');
    var ToDate = new Date();
    var d = new Date(a);

    var weekday = new Array(7);
    weekday[0] = "Sunday";
    weekday[1] = "Monday";
    weekday[2] = "Tuesday";
    weekday[3] = "Wednesday";
    weekday[4] = "Thursday";
    weekday[5] = "Friday";
    weekday[6] = "Saturday";

    var weekdays = weekday[d.getDay()];
    document.getElementById("weekdays").value = weekdays;

    if (weekdays != availabel_day[0] || d.getTime() <= ToDate.getTime() ) {
        alert('Choose Correct Weekday As Per Availabel Day Or Date Must Greater Today Date!!!!!');
        return false;
    }
    return true;
}

function myFunction_new() {                                                             //datetoday and compare(new)
    var a = document.getElementById("appointment_date1").value;
    var availabel_day_time = document.getElementById("available_day_new").value;
    var availabel_day = availabel_day_time.split(',');
    var ToDate = new Date();
    var d = new Date(a);
    var weekday = new Array(7);
    weekday[0] = "Sunday";
    weekday[1] = "Monday";
    weekday[2] = "Tuesday";
    weekday[3] = "Wednesday";
    weekday[4] = "Thursday";
    weekday[5] = "Friday";
    weekday[6] = "Saturday";

    var weekdays = weekday[d.getDay()];
    document.getElementById("weekdays1").value = weekdays;

    if (weekdays != availabel_day[0] || d.getTime() <= ToDate.getTime()) {
        alert('Choose Correct Weekday As Per Availabel Day Or Date Must Greater Today Date!!!!!');
        return false;
    }
    return true;
}

function shaowHidepatient(){
    if(document.getElementById("patient").checked){
         var data = document.getElementById("patient_form");
         if(data.style.display === 'none'){
            data.style.display = "block";
         }
         else{
            data.style.display = 'none';
         }
    }
}

function myChangeFunction(input1) {
    var input2 = document.getElementById('myInput2');
    input2.value = input1.value;
}



