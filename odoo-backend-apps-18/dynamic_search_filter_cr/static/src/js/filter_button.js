/** @odoo-module **/

//import { jsonrpc } from "@web/core/network/rpc_service";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
import { Component, xml } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { DomainSelectorDialog } from "@web/core/domain_selector_dialog/domain_selector_dialog";


patch(DomainSelectorDialog.prototype,{
    setup() {
        super.setup();
//        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.onApply_Custom = this.onApply_Custom.bind(this);
    },
    async onApply_Custom() {
    const domainString = this.state.domain;
    const fieldNameMatch = domainString.match(/\(\s*("[^'"]+")\s*,\s*("[^'"]+")\s*,/);

    if (fieldNameMatch) {
        const fieldName = fieldNameMatch[1].replace(/"/g, '');
        const operator = fieldNameMatch[2].replace(/"/g, '');

        var output_field = fieldName;
        var output_operator = operator;

        // Check if the URL contains 'odoo' to get action_id
        if (window.location.href.includes('odoo')) {
            var url = new URL(window.location.href);
            var action_id = url?.pathname?.split('/')?.filter(Boolean)[1];
        }

        // Proceed if action_id is available
        if (action_id) {
            await rpc("/dynamicfiltermodel/view", {
                data: {
                    'action_id': action_id,
                    'res_model': this.props.resModel,
                    'field_string': output_field,
                    'operator': output_operator,
                }
            }).then(function (a) {
                window.location.reload();
            });
        }
    } // End of fieldNameMatch check

} // End of onApply_Custom function

});

