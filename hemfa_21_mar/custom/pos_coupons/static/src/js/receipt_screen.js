odoo.define("pos_coupons.receipt_screen", function (require) {
    "use strict";

    const ReceiptScreen = require("point_of_sale.ReceiptScreen");
    const Registries = require("point_of_sale.Registries");
    var rpc = require('web.rpc');

    const PosReceiptScreen = (ReceiptScreen) =>
        class extends ReceiptScreen {

        };

    Registries.Component.extend(ReceiptScreen, PosReceiptScreen);
});
