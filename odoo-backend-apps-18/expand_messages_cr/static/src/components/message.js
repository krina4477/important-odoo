/** @odoo-module **/

import { Message } from '@mail/core/common/message';
import { patch } from "@web/core/utils/patch";
import { useRef } from "@odoo/owl";
import { useState } from "@odoo/owl";
import { Component } from "@odoo/owl";


patch(Message.prototype, {
	setup() {
		super.setup();
	},
	_onClickMessageCollapseMore(ev) {
		var elements = [ev.currentTarget.parentNode]
		elements.forEach((rec)=>{
		    rec.innerText = rec.firstElementChild.innerText
		})
	},

});
