/** @odoo-module **/

import { registry } from "@web/core/registry";
import { textField, TextField } from "@web/views/fields/text/text_field";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { dialog_field } from "./dialog";
import { dialog_field_del } from "./dialog";


import { onWillUpdateProps, onWillStart,onMounted } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { Field } from "@web/views/fields/field";
import { useService } from "@web/core/utils/hooks";

import { FormStatusIndicator } from "@web/views/form/form_status_indicator/form_status_indicator";
import { Component } from "@odoo/owl";

export class FieldTextTableWidget extends TextField {

    setup() {
        super.setup();

        this.env.model.root.dirty = true
        this.dialog = useService("dialog")
        onWillUpdateProps(this.willUpdate);
        onMounted(this.onMounted)

    }

    onMounted() {
        if(this.textareaRef && this.textareaRef.el){
            this._TextrenderReadonly(this.props);
        }
    }

    async willUpdate(nextProps) {
        if(this.textareaRef && this.textareaRef.el){
            this._TextrenderReadonly(nextProps);
        }

    }

    async _TextrenderReadonly(nextProps, extractProps) {
        var self = this;

        var format_val = nextProps || nextProps.value;

        var isHTML = RegExp.prototype.test.bind(/(<([^>]+)>)/i);
        $(self.textareaRef.el).parent().find('table#text_table').remove();
        if ($(this.props.record.data.x_website_description).find('td')){
             var str_table = '<table class="table table-striped table-bordered" id="text_table">' +
                    '<thead>' +
                    '<tr class="text_table_thead"><th class="text_table_thead_th text-center" scope="col"><a title="Click On" class="text_table_td_add_button" href="#" role="button">Add a col</a></th></tr>' +
                    '</thead><tbody>' +
                    '<tr class="text_table_tr_last"><td class="text_table_th_last text-center" t-on-click="add_line" ><a title="Click On"class="text_table_tr_add_button" href="#" role="button">Add a line</a></td></tr>' +
                    '</tbody></table>';

            $(self.textareaRef.el).css('display', 'none');
            $(self.textareaRef.el).after(this.props.record.data.x_website_description || str_table );
            self._table_td_add_button($(self.textareaRef.el).parent(), nextProps, this.props.record.data.x_website_description);
        }
        else if (format_val && isHTML(format_val) && $(format_val).find('thead').length > 0) {
            $(self.textareaRef.el).css('display', 'none');
            $(self.textareaRef.el).after(format_val);
            self._table_td_add_button($(self.textareaRef.el).parent(), nextProps);
        } else {
            if ($('td').length  === 0) {

                var str_table = '<table class="table table-striped table-bordered" id="text_table">' +
                    '<thead>' +
                    '<tr class="text_table_thead"><th class="text_table_thead_th text-center" scope="col"><a title="Click On" class="text_table_td_add_button" href="#" role="button">Add a col</a></th></tr>' +
                    '</thead><tbody>' +
                    '<tr class="text_table_tr_last"><td class="text_table_th_last text-center" t-on-click="add_line" ><a title="Click On"class="text_table_tr_add_button" href="#" role="button">Add a line</a></td></tr>' +
                    '</tbody></table>';

                $(self.textareaRef.el).css('display', 'none');
                $(self.textareaRef.el).after(str_table);
                self._table_td_add_button($(self.textareaRef.el).parent(), nextProps, str_table);
            }
        }
    }
    _table_td_add_button($el, nextProps, str_table,extractProps) {
        var self = this;



        $el.find('thead .t_all_th .close').off("click");
        $el.find('thead .t_all_th .close').on('click', function (b) {

        self.dialog.add(ConfirmationDialog,
         {
            body: _t('Do you really want to delete ""?'),
            cancel: () => {},
            confirm: () =>
            {

                var columnIndex = $(b.currentTarget).parent().index();
                        $el.find('tr').each(function() {
                            $(this).find('td').eq(columnIndex).remove();
                        });
                        $(b.currentTarget).parent().remove();
            },
         });

        });


        $el.find('.text_table_tr_del_button').off("click");
        $el.find('.text_table_tr_del_button').on('click', function (b) {
        self.dialog.add(ConfirmationDialog, {
            body: _t('Do you really want to delete ""?'),
            cancel: () => {},
            confirm: () => b.currentTarget.parentElement.parentElement.remove(),
        })
        });


        $el.find('.text_table_tr_add_button').off("click");
        $el.find('.text_table_tr_add_button').click(function(e){
            var $tr = $(e.currentTarget).parent().parent();
            var seq_number = $tr.parent().find('tr:not(.text_table_tr_last)').length
            seq_number = seq_number + 1;
            var str_td = '<td class="text-center"><a title="Delete" class="text_table_tr_del_button fa fa-trash" href="#" role="button"/></td>';
            $.each($tr.parent().parent().find('thead th:not(.text_table_thead_th)'),function(val){
                var col_type = $(this).data('type');
                var timestamp = $(this).data('ts');
                str_td += '<td data-ts="'+timestamp+'" data-type="'+col_type+'"><input type="'+col_type+'"/>'+'</td>';
            });
            $tr.before('<tr>'+str_td+'</tr>');
            var str_table = $tr.parent().parent().html();
            if(str_table){

                 $('<table class="table table-striped table-bordered" id="text_table">'+ str_table +'</table>');
                self._table_td_add_button($(self.textareaRef.el).parent(), nextProps);

            }
        });

        var self = this
        $el.find('.text_table_td_add_button').off("click");
        $el.find('.text_table_td_add_button').click(function(e){


            self.dialog.add(dialog_field, {
                cancel : ()=>{},

            })
        });

        $el.find("tbody input").off("change");
        $el.find("tbody input").change(function() {
            if(this.type == 'checkbox'){
                if(this.checked){
                    $(this).attr('checked','checked')
                }else{
                    $(this).removeAttr('checked');
                }
                var str_table = $(self.textareaRef.el).parent().find('#text_table').html();

                if(str_table){
                   $('<table class="table table-striped table-bordered" id="text_table">'+ str_table +'</table>');

                }
            }else{
                $(this).attr("value", $(this).val());
                var str_table = $(self.textareaRef.el).parent().find('#text_table').html();
                if(str_table){
                   $('<table class="table table-striped table-bordered" id="text_table">'+ str_table +'</table>');

                }
            }
        });
    }



}
FieldTextTableWidget.Component = {
FormStatusIndicator
}

export const htmlField = {
    ...textField,
    component: FieldTextTableWidget,

};

registry.category("fields").add("dynamic_table", htmlField);


