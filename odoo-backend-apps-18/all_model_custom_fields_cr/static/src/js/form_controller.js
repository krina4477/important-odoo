/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { session } from '@web/session';
import { useService } from "@web/core/utils/hooks"
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";


patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
    },

    getStaticActionMenuItems() {
        const custom = super.getStaticActionMenuItems();
    
            if (session.group_global_custom_field) {

                    custom.customField = {
                        icon: "fa fa-code",
                        sequence: 60,
                        description: _t("Add Custom Field"),
                        callback: () => this._onCreateCustomField(),
                    },
                    
                    custom.customTab =  {
                        icon: "fa fa-file-text-o",
                        sequence: 70,
                        description: _t("Add Custom Tab"),
                        callback: () => this._onCreateCustomTab(),
                    }
            }
        return custom
    },
    
    _onCreateCustomTab: async function (data) {
        await this.model.mutex.getUnlockedDef();
        var context = { ...this.model.config.context };

        const viewId = this.env.config.viewId;

        if (this.model.config.resModel) {
            const modelId = await this.orm.searchRead("ir.model", [['model', '=', this.model.config.resModel]], ['id'])
            const xml_id = await this.orm.searchRead("ir.ui.view", [['id','=', viewId]], ['id'])
            
            context['default_xml_id'] =  xml_id[0]['id'] || null;
            context['default_model_id'] = modelId[0] || null;
            context['default_is_custom_tab'] = true;
        }

    this.model.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'create.custom.tab',
            views: [[false, "form"]],
            view_mode: "form",
            target: "new",
            context: context,
        }, {
            onClose: () => {
                browser.location.reload();
            },
        });
    },

    _onCreateCustomField: async function (data) {
        await this.model.mutex.getUnlockedDef();
        var context = { ...this.model.config.context };
        if (this.model.config.resModel) {
            const modelId = await this.orm.searchRead("ir.model", [['model', '=', this.model.config.resModel]], ['id'])

            context['default_model_id'] = modelId[0] || null;
            context['default_is_custom_field'] = true;
        }

        this.model.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'ir.model.fields',
            views: [[false, "form"]],
            view_mode: "form",
            target: "new",
            context: context,
        });

    },
})