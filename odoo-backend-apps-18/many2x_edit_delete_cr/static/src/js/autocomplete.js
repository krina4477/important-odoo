/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";
import { session } from "@web/session";
import { sprintf } from "@web/core/utils/strings";


patch(Many2XAutocomplete.prototype, {
    setup() {
        super.setup();
    },
    async loadOptionsSource(request) {
        if (this.lastProm) {
            this.lastProm.abort(false);
        }
        this.lastProm = this.search(request);
        const records = await this.lastProm;
        const options = records.map((result) => ({
            value: result[0],
            label: result[1] ? result[1].split("\n")[0] : _t("Unnamed"),
            displayName: result[1],
            model: this.props.resModel,
            canEdit: this.props.context.can_edit,
            canDelete: this.props.context.can_delete,
        }));


        if (this.props.quickCreate && request.length) {
            options.push({
                label: _t('Create "%s"', request),
                classList: "o_m2o_dropdown_option o_m2o_dropdown_option_create",
                action: async (params) => {
                    try {
                        await this.props.quickCreate(request, params);
                    } catch (e) {
                        if (
                            e instanceof RPCError &&
                            e.exceptionName === "odoo.exceptions.ValidationError"
                        ) {
                            const context = this.getCreationContext(request);
                            return this.openMany2X({ context });
                        }
                        throw e;
                    }
                },
            });
        }

        if (!this.props.noSearchMore && records.length > 0) {
            options.push({
                label: _t("Search More..."),
                action: this.onSearchMore.bind(this, request),
                classList: "o_m2o_dropdown_option o_m2o_dropdown_option_search_more",
            });
        }

        const canCreateEdit =
            "createEdit" in this.activeActions
                ? this.activeActions.createEdit
                : this.activeActions.create;
        if (!request.length && !this.props.value && (this.props.quickCreate || canCreateEdit)) {
            options.push({
                label: _t("Start typing..."),
                classList: "o_m2o_start_typing",
                unselectable: true,
            });
        }

        if (request.length && canCreateEdit) {
            const context = this.getCreationContext(request);
            options.push({
                label: _t("Create and edit..."),
                classList: "o_m2o_dropdown_option o_m2o_dropdown_option_create_edit",
                action: () => this.openMany2X({ context }),
            });
        }

        if (!records.length && !this.activeActions.createEdit && !this.props.quickCreate) {
            options.push({
                label: _t("No records"),
                classList: "o_m2o_no_result",
                unselectable: true,
            });
        }

        return options;
    }
});

patch(Many2XAutocomplete,{
    props: {
        ...Many2XAutocomplete.props,
        canEdit: { type: Boolean, optional: true },
        canDelete: { type: Boolean, optional: true },
    },
    defaultProps:{
        ...Many2XAutocomplete.defaultProps,
        canEdit: false,
        canDelete: false,
    }
});


patch(AutoComplete.prototype, {
    setup() {
        super.setup();
    },
    OndeleteBtnClick(option){
        var self = this;
        var btn_id = option.value
        var model = option.model
        jsonrpc('/ondeletebtnclick', {delete_id: btn_id,model_name:model}).then((condition) => {
            if(condition == true){
                 window.location.reload();
            }
         });
    },
    OneditBtnClick(option){
        var self = this;
        var model = option.model
        var btn_id = option.value
        return self.env.services.action.doAction({
            res_model: model,
            res_id: parseInt(btn_id),
            name: _t("Open"),
            type: "ir.actions.act_window",
            views: [[false, "form"]],
            view_mode: "form",
            target: "new",
        });
    },
});
