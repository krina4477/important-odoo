/** @odoo-module **/

import { Pager } from "@web/core/pager/pager";
import { Component, useExternalListener, useState } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";

patch(Pager.prototype,{
    setup()
    {
        super.setup();
    },
     _showAll(ev) {
        const target = ev.currentTarget;

        if (target.classList.contains('o_pager_show_all')) {
            this.setValue("1-" + this.props.total);
            target.textContent = "Reset";
            target.classList.remove('o_pager_show_all');
        } else {
            target.textContent = "Show All";
            target.classList.add('o_pager_show_all');
            this.setValue('1-80');
        }
    }
});