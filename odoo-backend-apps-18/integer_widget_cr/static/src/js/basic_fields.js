/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { registry } from "@web/core/registry";
import { IntegerField } from "@web/views/fields/integer/integer_field";
import { useInputField } from "@web/views/fields/input_field_hook";
import { parseInteger  } from "@web/views/fields/parsers";
import { formatInteger } from '@web/views/fields/formatters';
import { _t } from "@web/core/l10n/translation";

patch(IntegerField.prototype, {
    setup() {
		super.setup();
		this.formatInteger = formatInteger;
      },
	get formattedValue() {
        var name= this.props.name
        if (this.props.formatNumber) {
	        var activeFields = this.props.record.activeFields
	        var name = this.props.name
 	        var optionsString = activeFields[this.props.name].context
            let temp = optionsString.replace(/'/g, '"');
            var options = JSON.parse(temp);

	        if (options['color'] && options['condition'] && options['value']) {
                var condition = parseInt(this.props.record.data[name]) + options['condition'] + parseInt(options['value']);
	            if (eval(condition)) {
	                this.__owl__.refs.numpadDecimal.style.backgroundColor = options['color'];
	            }
	            else {
		            if (options['else']) {
		                this.__owl__.refs.numpadDecimal.style.backgroundColor = options['else'];
		            }
		            else {
		                this.__owl__.refs.numpadDecimal.style.backgroundColor = 'transparent';
		            }
	            }
	        }
        }


        if (!this.props.readonly && this.props.inputType === "number") {
            return this.props.record.data[name];
        }

        return this.formatInteger(this.props.record.data[name]);
    }
});


