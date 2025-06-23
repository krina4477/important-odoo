/** @odoo-module */

import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";

import { Component } from "@odoo/owl";


export class dialog_field extends Dialog {

    setup() {
    console.log("setup call",this)
        super.setup()
    }

    async _cancel() {
        this.props.close();
    }

    async _confirm() {
        this.props.save();
    }



    async add_button(e) {
        var col_type = $("input[type='radio']:checked").val() || 'text';
        var col_name = $("input.column_sequence_input").val() || col_type;
        var timestamp = new Date().getTime();
        var column = '<th title="' + col_name + '" data-ts="' + timestamp + '" scope="col" class="t_all_th" data-type="' + col_type + '"><span title="Delete" class="close">&times;</span>' + col_name + '</th>';
        $('thead th:last-child').after(column);

        if ($('tbody tr:not(.text_table_tr_last)').length > 0) {
            $('tbody tr:not(.text_table_tr_last)').each(function() {
                $(this).append('<td data-ts="' + timestamp + '" data-type="' + col_type + '"><input type="' + col_type + '"/></td>');
            });
        }

          var $table = $(e.currentTarget).parent().parent().parent().parent();
//        var $table = $(e.currentTarget).closest('table');
        var str_table = $table.html();
        if (str_table) {

            $('<table class="table table-striped table-bordered" id="text_table">' + str_table + '</table>');

        }

        this.props.close();
    }

}
dialog_field.template = "text.table.td.add";
dialog_field.components = {
    Dialog ,
 };



dialog_field.props = {
    close: Function,

   confirm: { type: Function, optional: true },
   cancel: { type: Function, optional: true },
   add_button:{ type: Function, optional: true },
};
dialog_field.defaultProps = {
    confirmLabel: _t("Ok"),
    cancelLabel: _t("Cancel"),
    confirmClass: "btn-primary",
    title: _t("Add Column"),

};


//delete dialog
export class dialog_field_del extends Dialog{
    setup() {
    }

    async _cancel() {
        this.props.close();
    }

    async _confirm() {
        this.props.save();

    }

}
dialog_field_del.template = "text.table.td.delete";
dialog_field_del.components = { Dialog,
 };

dialog_field_del.props = {
    close: Function,
    confirm: { type: Function, optional: true },
    cancel: { type: Function, optional: true },
};
dialog_field_del.defaultProps = {
    confirmLabel: _t("Ok"),
    cancelLabel: _t("Cancel"),
    confirmClass: "btn-primary",
    title: _t("Delete"),
};



