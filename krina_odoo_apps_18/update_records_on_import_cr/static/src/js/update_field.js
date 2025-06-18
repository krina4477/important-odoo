/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { SelectMenu } from "@web/core/select_menu/select_menu";

patch(SelectMenu.prototype, {
    FileUploadData(){
        document.querySelectorAll('.o_import_update_option').forEach(function(el) {
            el.addEventListener('change', function(ev) {
                if (this.checked) {
                    document.querySelectorAll('.o_import_update_option').forEach(function(otherEl) {
                        if (otherEl !== el) {
                            otherEl.checked = false;
                        }
                    });
                }
            });
        });
    }
    
})