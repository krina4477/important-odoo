/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Many2ManyTagsField } from "@web/views/fields/many2many_tags/many2many_tags_field";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Many2ManyTagsFieldColorEditable } from "@web/views/fields/many2many_tags/many2many_tags_field";


patch(Many2ManyTagsFieldColorEditable,{
    props: {
        ...Many2ManyTagsField.props,
        canEditColor: { type: Boolean, optional: true },
        canEdit :{ type: Boolean, optional: true },
        canDelete :{ type: Boolean, optional: true },
    },
    defaultProps : {
        ...Many2ManyTagsField.defaultProps,
        canEditColor: true,
        canEdit: false,
        canDelete: false,
    },
    extractProps({ options }) {
        const props = many2ManyTagsField.extractProps(...arguments);
        props.canEditColor = !options.no_edit_color && !!options.color_field;
        props.canEdit = options.can_edit;
        props.canDelete = options.can_delete;
        return props;
    },

});


patch(Many2ManyTagsField,{
    props: {
        ...Many2ManyTagsField.props,
        canEdit :{ type: Boolean, optional: true },
        canDelete :{ type: Boolean, optional: true },
    },
    extractProps({ attrs, options, string }, dynamicInfo) {
        const noCreate = Boolean(options.no_create);
        const canCreate = noCreate
            ? false
            : attrs.can_create && evaluateBooleanExpr(attrs.can_create);
        const noQuickCreate = Boolean(options.no_quick_create);
        const noCreateEdit = Boolean(options.no_create_edit);
        return {
            colorField: options.color_field,
            nameCreateField: options.create_name_field,
            canCreate,
            canQuickCreate: canCreate && !noQuickCreate,
            canCreateEdit: canCreate && !noCreateEdit,
            createDomain: options.create,
            context: dynamicInfo.context,
            domain: dynamicInfo.domain,
            placeholder: attrs.placeholder,
            string,
            canEdit,
            canDelete,
        };
    },

});



