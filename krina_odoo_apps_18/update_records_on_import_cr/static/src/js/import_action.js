/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { BaseImportModel } from "@base_import/import_model"


patch(BaseImportModel.prototype, {
    async _callImport(dryrun, args) {
        const checkedOption = document.querySelector('.o_import_update_option:checked');

        if (checkedOption) {
            this.importOptionsValues['field_to_check'] = {
                'field_to_check': checkedOption.value
            };

            try {
                const fieldIcon = checkedOption.closest('td').querySelector('.o_import_field_icon');
                const tooltipInfo = fieldIcon.getAttribute('data-tooltip-info');
                const field_name = JSON.parse(tooltipInfo).field.name;

                const res = await this.orm.silent.call("base_import.import", "execute_import", args, {
                    dryrun,
                    context: { 'field_to_check': field_name }
                });

                return res;
            } catch (error) {
                // Handle import errors and show them inside the "messages" area
                return { error };
            }
        } else {
            console.error('No option is selected. Please select an option.');
            return { error: 'No option is selected' };
        }

    }
})
