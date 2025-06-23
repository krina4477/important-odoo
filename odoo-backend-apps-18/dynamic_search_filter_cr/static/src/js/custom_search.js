/** @odoo-module **/

import { ModelFieldSelectorPopover } from "@web/core/model_field_selector/model_field_selector_popover";
import { useService } from "@web/core/utils/hooks";
import { Component, xml } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";

patch(ModelFieldSelectorPopover.prototype,{
    setup() {
    super.setup();
    },
    openPopover(currentTarget) {
        if (this.props.readonly) {
            return;
        }
        this.newPath = null;
        this.popover.open(currentTarget, {
            resModel: this.props.resModel,
            path: this.props.path,
            update: (path, debug = false) => {
                this.newPath = path;
                if (!debug) {
                    this.updateState({ ...this.props, path }, true);
                }
            },
            showSearchInput: this.props.showSearchInput,
            isDebugMode: this.props.isDebugMode,
            filter: this.props.filter,
            followRelations: this.props.followRelations,
            showDebugInput: this.props.showDebugInput,
        });
    }
});