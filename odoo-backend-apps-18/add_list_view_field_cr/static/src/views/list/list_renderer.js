/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { rpc } from "@web/core/network/rpc";

patch (ListRenderer.prototype,{

    _onAddField: function(ev) {
        let selectedFields = Array.from(document.querySelectorAll('input.field-checkbox:checked')).map(cb => cb.value);
        if (selectedFields.length > 0 && ev.env.config.viewType === 'list') {
            rpc(`/web/dataset/call_kw/ir.ui.view/add_field`, {
                model: 'ir.ui.view',
                method: 'add_field',
                args: [ev.env.config.viewId, selectedFields, ev.props.list.resModel],
                kwargs: {},
            }).then(function(id) {
                window.location.reload()
            });
        }
    },

    onSelectedAddNewField() {
        var field_list = [];
        (this.getOptionalFields, function(field) {
            field_list.push(field.name)
        });
        var self = this
        rpc('/add_field', {
            kwargs: {
                'model': this.props.list.resModel
            },
        }).then(function(fields) {
            let fieldSelector = document.querySelector('.field-selector');
            if (fieldSelector) {
                fieldSelector.innerHTML = '';
                fields.forEach((field, index) => {
                    let option = document.createElement('span');
                    option.className = 'o-dropdown-item dropdown-item o-navigable';
                    option.setAttribute('role', 'menuitem');
                    option.setAttribute('tabindex', '0');
                    option.innerHTML = `
                        <div class="o-checkbox form-check">

                            <label class="form-check-label">
                                <input type="checkbox" class="form-check-input field-checkbox" id="checkbox-comp-${index}" name="${field[0]}" value="${field[0]}">
                                <span class="d-flex align-items-center">
                                    <span class="text-truncate">${field[1]}</span>
                                    <span class="ps-1"> (${field[0]})</span>
                                </span>
                            </label>
                        </div>
                    `;
                    fieldSelector.appendChild(option);
                });
                fieldSelector.classList.remove('d-none');
            }

            let addField = document.getElementsByClassName("o_Add_field");
            for (let i = 0; i < addField.length; i++) {
                addField[i].classList.remove('d-none');
            }
        });
    },
})