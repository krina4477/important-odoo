/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";


    publicWidget.registry.SignUpForm.include({
    

        _onSubmit: function (event) {           
            var recaptchaResponse = grecaptcha.getResponse();
            if (recaptchaResponse.length === 0) {
                // Show an alert or highlight the reCAPTCHA field to inform the user                          
                $("input[name='g-recaptcha-response']").val(recaptchaResponse)                
                alert('Please complete the reCAPTCHA');
                event.preventDefault(); // Prevent form submission
            }
            else {
                $("input[name='g-recaptcha-response']").val(recaptchaResponse)  
                return this._super();
            }            
        },       

    })
