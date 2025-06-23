/** @odoo-module **/

import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(SelectCreateDialog.prototype,{
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
    },

    async OndeleteRecord(resIds) {
         var self = this
         if (resIds.length){
            this.dialogService.add(ConfirmationDialog, {
                body: _t("Are you sure you want to delete ?"),
                confirmLabel: _t("Yes"),
                confirm: () => {
                    this.env.services.orm.unlink(this.props.resModel, Array.from(resIds));
                    window.location.reload();
                },
                cancel: () => {},
            });
        }
    },
});

