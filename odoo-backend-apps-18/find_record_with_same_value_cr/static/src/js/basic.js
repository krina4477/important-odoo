/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";
import { renderToElement } from "@web/core/utils/render";
import { usePopover } from "@web/core/popover/popover_hook";
const fieldsRegistry = registry.category("fields");
import { Component } from "@odoo/owl";
import { localization } from "@web/core/l10n/localization";

class FieldPopOver extends Component {
    static props = { "*": { optional: true } ,popup: { type: Object}};
    static template = "find_record_with_same_value_cr.DuplicateRecordPopOver";
}

class CharFieldTableWidget extends CharField {
    setup() {
        super.setup();
        const position = localization.direction === "rtl" ? "bottom" : "top";
        this.popover = usePopover(FieldPopOver, { position });
    }

    parse(value) {
        var self = this;
        if (this.input.el.parentNode.classList.contains('o_field_show_duplicate_rec')) {
            var resModel = this.props.record.resModel;
            var activeFields = this.props.record.activeFields;
            var options = activeFields[this.props.name].context;
            var recId = this.props.record.resId;
            setTimeout(function () {
                self.input.el.parentNode.classList.add('d-flex');
                var str_show_div = '<div class="pl-3 show_widget">' +
                                '<button class="fa fa-search-plus text-danger show_duplicate_rec"></button></div>';
                if (document.getElementsByClassName('show_duplicate_rec').length == 0){
                    self.input.el.parentNode.insertAdjacentHTML('beforeend', str_show_div);
                }
                var showDuplicateButton = document.getElementsByClassName('show_duplicate_rec')[0];

                if (showDuplicateButton) {
                    showDuplicateButton.addEventListener('click', function(ev) {
                        var oFieldShowDuplicateRec = document.getElementsByClassName('o_field_show_duplicate_rec')[0];
                        if (resModel && options && (oFieldShowDuplicateRec && oFieldShowDuplicateRec.children[0].value) || recId) {
                            rpc('/finds_records', {
                                model: 'base',
                                method: 'fetch_duplicate_record',
                                kwargs: {
                                    'fields_name': self.props.name,
                                    'model_name': resModel,
                                    'rec_id': recId,
                                    'val': oFieldShowDuplicateRec.children[0].value,
                                    'options': options
                                },
                            }).then(function(popup_show) {
                                self.popover.open(showDuplicateButton, {
                                    target :showDuplicateButton,
                                    popup: popup_show,
                                    title: _t('Show Duplicate Value Record'),
                                });

                                setTimeout(function() {
                                    document.querySelectorAll('.action_redirect_view').forEach(function(el) {
                                        el.addEventListener('click', function(ev) {
                                            if (popup_show) {
                                                return self.env.services['action'].doAction({
                                                    name: _t('Show Duplicate Value Record'),
                                                    type: 'ir.actions.act_window',
                                                    target: 'current',
                                                    res_model: popup_show[0]['model'],
                                                    views: [[false, 'list'], [false, 'form']],
                                                    domain: [[popup_show[0]['dyn_field'], 'ilike', popup_show[0]['dyn_value']]],
                                                    context: {},
                                                });
                                            }
                                        });
                                    });
                                }, 100);
                            });
                        }
                    });
                }
            }, 300);
        }
        if (this.props.shouldTrim) {
            return value.trim();
        }
        return value;
    }
}

fieldsRegistry.add("show_duplicate_rec", { component: CharFieldTableWidget });