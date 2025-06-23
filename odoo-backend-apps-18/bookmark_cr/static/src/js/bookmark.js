/** @odoo-module */

import { ActivityMenu } from "@mail/core/web/activity_menu";
import { patch } from "@web/core/utils/patch";
import { deserializeDateTime, formatDateTime } from "@web/core/l10n/dates";
import { localization } from "@web/core/l10n/localization";

patch(ActivityMenu.prototype, {
    _onBookmarkClick: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this.env.services.action.doAction({
            name: "Bookmarks",
            res_model: "bookmark.bookmark",
            views: [[false, "list"], [false, "form"]],
            type: "ir.actions.act_window",
            view_mode: "form",
        });
    },
});