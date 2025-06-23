
/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { FormController } from '@web/views/form/form_controller';
import { _t } from "@web/core/l10n/translation";
//import { jsonrpc } from "@web/core/network/rpc_service";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";

patch(FormController.prototype, {
    setup() {
        super.setup();
//        this.rpc = useService("rpc");
    },
    get actionMenuItems() {
        const actionToKeep = ["archive", "unarchive", "duplicate", "delete"];
        const menuItems = super.actionMenuItems;
        const filteredActions =
            menuItems.action?.filter((action) => actionToKeep.includes(action.key)) || [];

        var blank_dict = {
            [this.props.resModel]: []
        }
        if (!Object.keys(session.model_bookmarks).includes(this.props.resModel)) {
            session.model_bookmarks = Object.assign({}, session.model_bookmarks, blank_dict);
        }
        var bookmark = false
        if (session.model_bookmarks && session.model_bookmarks[this.props.resModel] && session.model_bookmarks[this.props.resModel].includes(this.props.resId)) {
            bookmark = true
        }
        if (!bookmark) {
            filteredActions.push({
                description: _t("Add to Bookmark"),
                callback: () => {
                    this._onBookmarkRecord(this)
                },
            });
        }
        if (bookmark) {
            filteredActions.push({
                description: _t("Remove Bookmark"),
                callback: () => {
                    this._onRemoveBookmarkRecord(this)
                },
            });
        }
        menuItems.action = filteredActions;
        return menuItems
    },
    _onBookmarkRecord: function (ev) {
        var self = this
        rpc('/form_create', {
            kwargs: {
                'name': 'Bookmark for' + " " + this.model.root.resModel,
                'model': this.model.root.resModel,
                'record_id': this.props.resId,
                'res_id': this.model.root.data.id,
                'user_id': session.uid
            },
        }).then((data) => {
            self.env.services.action.doAction({
                type: "ir.actions.client",
                tag: "display_notification",
                params: { message: "Bookmark Successfully", type: 'success', sticky: false }
            });
            var new_list = []
            new_list = session.model_bookmarks[self.env.searchModel.resModel]
            new_list.push(data)

            var source = {
                [self.env.searchModel.resModel]: new_list
            }
            session.model_bookmarks = Object.assign({}, session.model_bookmarks, source);
            window.location.reload();
        });

    },
    _onRemoveBookmarkRecord: function (ev) {
        var self = this;

        rpc('/formview_remove', {
            'model': self.model.root.resModel,
            'id': self.model.root.resId
        }).then(() => {
            self.env.services.action.doAction({
                type: "ir.actions.client",
                tag: "display_notification",
                params: { message: "Bookmark Removed Successfully", type: 'success', sticky: false }
            });
            var new_list = []
            var get_list = []
            new_list = session.model_bookmarks[self.env.searchModel.resModel]
            $.each(new_list, function (val) {
                if (new_list !== val) {
                    get_list.push(val)
                }

                var source = {
                    [self.env.searchModel.resModel]: get_list
                }
                session.model_bookmarks = Object.assign({}, session.model_bookmarks, source);

                window.location.reload();
            });
        });
    },
});