/** @odoo-module **/
import { FormStatusIndicator } from "@web/views/form/form_status_indicator/form_status_indicator";

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(FormStatusIndicator.prototype, {

     setup(){
        super.setup()
        this.orm = useService("orm");
    },

    async save() {
        var str_table = $('#text_table').html();
        if(this.props.model.config.resModel=='product.template')
        {
                 var table = ''
                 var model='product.template'
                 var resid=this.props.model.config.resId
                 var str_table = $('#text_table').html();
                 if(str_table){
                   table = ('<table class="table table-striped table-bordered" id="text_table">'+ str_table +'</table>');
                }
                 await this.orm.call(
                    'product.template',
                    'save',
                    [[],resid, table],
                    {}
                );
        }
         await this.props.save();
         window.location.reload();
    },
});