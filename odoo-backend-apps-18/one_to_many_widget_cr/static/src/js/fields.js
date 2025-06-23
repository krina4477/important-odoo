/** @odoo-module */

import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { registry } from "@web/core/registry";
import { session } from '@web/session';
import { rpc } from "@web/core/network/rpc";

export class FieldX2ManyField extends X2ManyField {
    export_to_excel(export_type) {
        var self = this;

        // Find Header Element
        var header_eles = document.querySelectorAll('.o_field_One2manyWidget table.o_list_table > thead th:not(.o_handle_cell)');
        var header_name_list = [];
        header_eles.forEach(header => {
            var text = header.textContent.trim() || "";
            var data_id = header.getAttribute('data-name');
            header_name_list.push({ 'header_name': text, 'header_data_id': data_id });
        });

        // Find Data Elements
        var data_eles = document.querySelectorAll('.o_field_One2manyWidget table.o_list_table > tbody > tr.o_data_row');
        var export_data = [];
        data_eles.forEach(data_ele => {
            var data = [];
            var is_header_group = data_ele.classList.contains('o_group_header');

            if (data_ele.textContent.trim()) {
                // Handle group header cells
                var group_th_eles = data_ele.querySelectorAll('th');
                group_th_eles.forEach(group_th => {
                    var text = group_th.textContent.trim() || "";
                    var padding_left = group_th.classList.contains('o_group_name') ? group_th.children[0].style.paddingLeft : '0px';

                    if (text) {
                        if (group_th.getAttribute('colspan') && parseInt(group_th.getAttribute('colspan')) > 1) {
                            data.push({ 'padding-left': padding_left, 'group_row': is_header_group, 'data': text, 'bold': true, 'colspan': group_th.getAttribute('colspan') });
                        } else {
                            data.push({ 'padding-left': padding_left, 'group_row': is_header_group, 'data': text, 'bold': true, 'colspan': 1 });
                        }
                    }
                });

                // Handle data cells
                var data_td_eles = data_ele.querySelectorAll('td:not(.o_handle_cell)');
                data_td_eles.forEach(data_td => {
                    var text = data_td.textContent.trim() || "";
                    if (data_td.classList.contains('o_list_record_selector')) {
                        data.push({ 'data': "", 'colspan': 1, 'group_row': false });
                    } else if (data_td.classList.contains('oe_number') && !data_td.classList.contains('oe_list_field_float_time')) {
                        text = text.replace('%', '');
                        text = parseFloat(text) || 0;

                        if (data_td.getAttribute('colspan') && parseInt(data_td.getAttribute('colspan')) > 1) {
                            data.push({ 'group_row': is_header_group, 'data': text, 'number': true, 'colspan': data_td.getAttribute('colspan') });
                        } else {
                            data.push({ 'group_row': is_header_group, 'data': text, 'number': true, 'colspan': 1 });
                        }
                    } else {
                        if (data_td.getAttribute('colspan') && parseInt(data_td.getAttribute('colspan')) > 1) {
                            data.push({ 'group_row': is_header_group, 'data': text, 'colspan': data_td.getAttribute('colspan') });
                        } else {
                            data.push({ 'group_row': is_header_group, 'data': text, 'colspan': 1 });
                        }
                    }
                });

                var data_length = data.reduce((sum, dt) => sum + parseInt(dt.colspan), 0);
                if (data_length < header_name_list.length) {
                    var rows_to_add = header_name_list.length - data_length;
                    for (var i = 0; i < rows_to_add; i++) {
                        data.push({ 'group_row': is_header_group, 'data': "" });
                    }
                }
                export_data.push(data);
            }
        });

        // Find Footer Element
        var footer_eles = document.querySelectorAll('.o_field_One2manyWidget table.o_list_table > tfoot > tr');
        footer_eles.forEach(footer_ele => {
            var data = [];
            var footer_td_eles = footer_ele.querySelectorAll('td');
            footer_td_eles.forEach(footer_td => {
                var text = footer_td.textContent.trim() || "";
                if (footer_td.classList.contains('oe_number')) {
                    text = parseFloat(text) || 0;
                    data.push({ 'data': text, 'bold': true, 'number': true });
                } else {
                    data.push({ 'data': text, 'bold': true });
                }
            });
            export_data.push(data);
        });

        if (export_type === 'excel') {
            rpc('/web/export/excel_export', {
                model: self.activeField.relation,
                headers: header_name_list,
                rows: export_data,
            }).then((response) => {
                if (response) {
                    // Create a link element to trigger the download
                    const link = document.createElement('a');
                    link.href = 'data:application/vnd.ms-excel;base64,' + response.file_content;
                    link.download = self.activeField.string + '.xlsx';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            }).catch((error) => {
                console.error('Error:', error);
                alert('Failed to export the file.');
            });
        }
    }
};

FieldX2ManyField.template = "one_to_many_widget_cr.One2manyTemplateCustom";

export const FieldX2ManyFieldCustom = {
    ...x2ManyField,
    component: FieldX2ManyField,
};
registry.category("fields").add("One2manyWidget", FieldX2ManyFieldCustom);
