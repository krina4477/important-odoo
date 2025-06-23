/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { ListController } from '@web/views/list/list_controller';
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
//import { jsonrpc } from "@web/core/network/rpc_service";
import { rpc } from "@web/core/network/rpc";

patch(ListController.prototype, {
    setup() {
        super.setup();
//        this.rpc = useService("rpc");
    },

    get actionMenuItems() {
        const actionToKeep = ["archive", "unarchive", "duplicate", "delete"];
        const isM2MGrouped = this.model.root.isM2MGrouped;
        const menuItems = super.actionMenuItems;
        const filteredActions =
            menuItems.action?.filter((action) => actionToKeep.includes(action.key)) || [];
        var blank_dict = {
            [this.props.resModel]: []
        }
        if (!Object.keys(session.model_bookmarks).includes(this.props.resModel)) {
            session.model_bookmarks = Object.assign({}, session.model_bookmarks, blank_dict);
        }
        var bookmark_list = []
        var without_bookmark_list = []
        var SelectRecord = this.model.root.selection
        $.each(SelectRecord, function (d) {
            if (session.model_bookmarks && session.model_bookmarks[d.resModel] && session.model_bookmarks[d.resModel].includes(d.resId)) {
                bookmark_list.push(d)
            } else {
                without_bookmark_list.push(d)
            }
        });
        if (without_bookmark_list.length > 0) {
            filteredActions.push({
                description: _t("Add to Bookmark"),
                callback: () => {
                    this._onBookmarkRecordList()
                },
            });
            
        }
        if (without_bookmark_list.length > 0) {
            filteredActions.push({
                description: _t("Remove Bookmark"),
                callback: () => {
                    this._onRemoveBookmarkRecordList()
                },
            });
        }
        menuItems.action = filteredActions;
        return menuItems
    },

    _onBookmarkRecordList: function (ev) {
        var self = this
        var get_ids = self.model.root.selection
        var id_list = []
        $.each(get_ids, function (id) {
            id_list.push(get_ids[id]._config.resId)
        });
        rpc('/list_create', {
            kwargs: {
                'name': 'Bookmark for' +" "+ self.props.resModel,
                'model': this.props.resModel,
                'new_ids': id_list,
                'user_id': session.uid,
            },
        }).then(() => {
            self.env.services.action.doAction({
                type: "ir.actions.client",
                tag: "display_notification",
                params: { message: "Bookmark Successfully", type: 'success', sticky: false }
            });
            var new_list = []
            var SelectRecord = self.model.root.selection
            $.each(SelectRecord, function (d) {
                new_list = session.model_bookmarks[self.model.root.resModel]
                new_list.push(d.resId)
            });
            var source = {
                [self.model.root.resModel]: new_list
            }
            session.model_bookmarks = Object.assign({}, session.model_bookmarks, source);
            window.location.reload();
        });
    },

    _onRemoveBookmarkRecordList: function (ev) {
        var self = this
        var get_ids = self.model.root.selection
        var id_list = []
        $.each(get_ids, function (id) {
            id_list.push(get_ids[id]._config.resId)
        });

        rpc('/listview_remove', {
            kwargs: {
                'model': this.props.resModel,
                'record_ids': id_list,
            },
            
        }).then(() => {
            self.env.services.action.doAction({
                type: "ir.actions.client",
                tag: "display_notification",
                params: { message: "Bookmark Removed Successfully", type: 'success', sticky: false }
            });
            var new_list = []
            var SelectRecord = id_list
            new_list = session.model_bookmarks[self.model.root.resModel]
            $.each(SelectRecord, function (d) {
                if (new_list.includes(d)) {
                    const index = new_list.indexOf(d);
                    if (index > -1) {
                        new_list.splice(index, 1); // 2nd parameter means remove one item only
                    }
                }
            });
            var source = {
                [self.model.root.resModel]: new_list
            }
            session.model_bookmarks = Object.assign({}, session.model_bookmarks, source);
            window.location.reload();
        });
    },
});