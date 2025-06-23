/** @odoo-module **/
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
/*var { busService } = require('@bus/services/bus_service');*/


export const webNotificationService = {
    dependencies: ["action", "notification", "bus_service"],

    start(env, { action, bus_service, notification }) {
        let webNotifTimeouts = {};

        bus_service.subscribe("account.move", (payload) => {
            displaywebNotification(payload);
        });
        bus_service.start();

        function displaywebNotification(notifications) {
            // let lastNotifTimer = 0;

            // Clear previously set timeouts and destroy currently displayed calendar notifications
            browser.clearTimeout(webNotifTimeouts);
            Object.values(webNotifTimeouts).forEach((notif) => browser.clearTimeout(notif));
            webNotifTimeouts = {};

            // For each notification, set a timeout to display it
            notifications.forEach(function (notif) {
                const key = notif.event_id + "," + notif.alarm_id;
                webNotifTimeouts[key] = browser.setTimeout(function () {
                    const notificationRemove = notification.add(notif.message, {
                        title: notif.title,
                        type: "warning",
                        sticky: notif.sticky,
                        className: notif.className,
                        buttons: [
                            {
                                name: _t("View Invoice"),
                                primary: true,
                                onClick: async () => {
                                    await action.doAction({
                                        type: 'ir.actions.act_window',
                                        res_model: 'account.move',
                                        res_id: notif.event_id,
                                        views: [[false, 'form']],
                                    })
                                },
                            },
                        ],
                    });
                }, notif.timer * 1000);
            });
        }
    },

};
registry.category("services").add("webNotification", webNotificationService);