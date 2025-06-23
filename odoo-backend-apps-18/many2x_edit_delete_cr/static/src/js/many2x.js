/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Many2OneField, many2OneField } from "@web/views/fields/many2one/many2one_field";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useChildRef, useOwnedDialogs, useService } from "@web/core/utils/hooks";

import { PartnerMany2XAutocomplete } from "@partner_autocomplete/js/partner_autocomplete_many2one";

patch(Many2OneField,{
    props: {
        ...Many2OneField.props,
        canEdit: { type: Boolean, optional: true },
        canDelete: { type: Boolean, optional: true },
    },
    defaultProps: {
        ...Many2OneField.defaultProps,
        canEdit: false,
        canDelete: false,
    },
    extractProps({ attrs, context, decorations, options, string }, dynamicInfo) {
        const canCreate =
            options.no_create ? false : attrs.can_create && evaluateBooleanExpr(attrs.can_create);
        return {
            placeholder: attrs.placeholder,
            canOpen: !options.no_open,
            canCreate,
            canWrite: attrs.can_write && evaluateBooleanExpr(attrs.can_write),
            canQuickCreate: canCreate && !options.no_quick_create,
            canCreateEdit: canCreate && !options.no_create_edit,
            context: context,
            decorations,
            domain: dynamicInfo.domain,
            nameCreateField: options.create_name_field,
            canScanBarcode: !!options.can_scan_barcode,
            string,
            canEdit: options.can_edit,
            canDelete: options.can_delete,
        };
    },

});


patch(Many2OneField.prototype, {
    setup() {
        super.setup();
    },
    get Many2XAutocompleteProps() {
        return {
            value: this.displayName,
            id: this.props.id,
            placeholder: this.props.placeholder,
            resModel: this.relation,
            autoSelect: true,
            fieldString: this.string,
            activeActions: this.state.activeActions,
            update: this.update,
            quickCreate: this.quickCreate,
            context: this.context,
            getDomain: this.getDomain.bind(this),
            nameCreateField: this.props.nameCreateField,
            setInputFloats: this.setFloating,
            autocomplete_container: this.autocompleteContainerRef,
            canEdit: false,
            canDelete: false,
        };
    },
});


patch(PartnerMany2XAutocomplete,{
	props: {
        ...PartnerMany2XAutocomplete.props,
        canEdit: { type: Boolean, optional: true },
        canDelete: { type: Boolean, optional: true },
    },
})