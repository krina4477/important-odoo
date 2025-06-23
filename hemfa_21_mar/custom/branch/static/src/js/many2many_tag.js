/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Many2ManyTagsField } from "@web/views/fields/many2many_tags/many2many_tags_field";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

const { onWillUpdateProps } = owl;

export class DeleteConfirmationDialog extends Many2ManyTagsField {
     async deleteTag(id) {
            const tagRecord = await this.props.value.records.find((record) => record.id === id);

           const action = await this.orm.call('product.template', "get_product_branch_id", [[this.props.record.data.id]], {
               branch: tagRecord.data.id,
         });
         if (action){
           const dialogProps = {
                            body: this.env._t("This branch may be available in variants. Are you sure that you want to remove this record?"),
                            confirmLabel: this.env._t("Delete"),
                            confirm: () => this.deleteTagRecord(id),
                            cancel: () => {},
                        };
          await this.dialog.add(ConfirmationDialog, dialogProps);


         }
         else{

            await this.deleteTagRecord(id);
         }



    }


    deleteTagRecord(id){

        const tagRecord = this.props.value.records.find((record) => record.id === id);
        const ids = this.props.value.currentIds.filter((id) => id !== tagRecord.resId);
        this.props.value.replaceWith(ids);
    }


}

registry.category("fields").add("delete_many2many_tags", DeleteConfirmationDialog);
