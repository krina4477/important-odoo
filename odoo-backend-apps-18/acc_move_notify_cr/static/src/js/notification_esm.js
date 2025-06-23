/** @odoo-module */
import { Component } from "@odoo/owl";

export class Notification extends Component {}
Notification.props = {
    type: {
        type: String,
        optional: true,
        validate: (t) => ["warning", "danger", "success", "info"].includes(t),
    },
 }
Notification.defaultProps = {
    buttons: [],
    className: "",
    type: "warning",
};