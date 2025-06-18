/** @odoo-module **/
//  Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
//  See LICENSE file for full copyright and licensing details.


import { ListRenderer } from "@web/views/list/list_renderer";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { Field } from "@web/views/fields/field";
import { ViewButton } from "@web/views/view_button/view_button";
import { CheckBox } from "@web/core/checkbox/checkbox";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { Pager } from "@web/core/pager/pager";
import { Widget } from "@web/views/widgets/widget";
import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { onRendered, useRef, useEffect, onMounted } from "@odoo/owl";

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        self.rootRef = useRef("root");
        self.tableRef = useRef("table");
        useEffect(() => {
            this.duplicaterendercolor();
        });
    },

    duplicaterendercolor() {
        if (this.props.list.resModel && session.show_duplicate_value_list && document.querySelectorAll('table.o_list_table').length > 0) {
            if (session.show_duplicate_value_list.hasOwnProperty(this.props.list.resModel)) {
                if (session.show_duplicate_value_list[this.props.list.resModel].length > 0) {
                    let isAllowDuplicateCom = false;
                    let count = 0;
                    const resModel = this.props.list.resModel;
                    const data = document.querySelectorAll('table.o_list_table > thead > tr > th');
                    const tableHeaders = Array.from(data);
                    const selectedFields = session.show_duplicate_value_list[resModel];

                    tableHeaders.forEach((header) => {
                        const backendFieldName = header.getAttribute('data-name');
                        selectedFields.forEach((field) => {
                            if (backendFieldName === field) {
                                count += 1;
                                isAllowDuplicateCom = true;
                                header.classList.add('duplifer-highlightdups' + count);
                            }
                        });
                    });

                    if (isAllowDuplicateCom) {
                        const table = document.querySelector('table.o_list_table');
                        table.setAttribute('data-dcount', count);
                        duplifer(table); // Call the `duplifer` function with the table element
                    }
                }
            }
        }
    }
});